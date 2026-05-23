import json
import os
import sys
from typing import Dict, Any, List, Optional

# Sentinel object to represent keys that did not exist before a transaction started
NO_VALUE = object()

class PredictiveCache:
    """
    Implements a First-Order Markov Chain Predictive Cache.
    Tracks sequential GET access patterns to build a transition matrix
    and predicts the most likely next key to be accessed.
    """
    def __init__(self) -> None:
        # transitions[prev_key][next_key] = count
        self.transitions: Dict[str, Dict[str, int]] = {}
        self.last_key: Optional[str] = None

    def record_access(self, key: str) -> None:
        """
        Records a state transition in the Markov Chain from self.last_key to key.
        Updates the internal state to make 'key' the new self.last_key.
        """
        if self.last_key is not None:
            if self.last_key not in self.transitions:
                self.transitions[self.last_key] = {}
            
            # Increment the transition count from last_key to the current key
            self.transitions[self.last_key][key] = self.transitions[self.last_key].get(key, 0) + 1

        self.last_key = key

    def predict(self, key: str) -> Optional[str]:
        """
        Predicts the next key likely to be accessed after the given key.
        Uses alphabetical order as a deterministic tie-breaker when transition counts are equal.
        """
        if key not in self.transitions or not self.transitions[key]:
            return None

        candidates = self.transitions[key]
        
        # We want to find the candidate key with the maximum count.
        # Tie-breaker: Alphabetically first key.
        # To achieve this: we sort by count descending, and key ascending.
        # e.g., sorted(candidates.items(), key=lambda x: (-x[1], x[0]))
        best_candidate = min(candidates.items(), key=lambda x: (-x[1], x[0]))
        return best_candidate[0]

    def predict_next(self, key: str) -> Optional[str]:
        """Alias for predict() to support test suites."""
        return self.predict(key)

    def format_telemetry(self) -> str:
        """
        Returns a beautifully formatted visualization of the Markov Chain transition matrix.
        """
        if not self.transitions:
            return "\033[90m(No transitions recorded yet)\033[0m"

        lines = ["\033[36m=== Markov Chain Transition Telemetry ===\033[0m"]
        for prev_key, next_keys in sorted(self.transitions.items()):
            total_transitions = sum(next_keys.values())
            lines.append(f"  \033[1m{prev_key}\033[0m (last visited, total exits: {total_transitions}):")
            
            # Sort destinations by count desc, then name asc
            sorted_destinations = sorted(next_keys.items(), key=lambda x: (-x[1], x[0]))
            for next_key, count in sorted_destinations:
                percentage = (count / total_transitions) * 100
                lines.append(f"    -> \033[32m{next_key}\033[0m (count: {count}, probability: {percentage:.1f}%)")
        return "\n".join(lines)


class SpreeDB:
    """
    SpreeDB: An in-memory key-value database engine with nested transactions,
    O(1) value frequency counts, and predictive prefetch caching.
    """
    def __init__(self) -> None:
        # Live state representing the active database state
        self.db: Dict[str, Any] = {}
        
        # Tracks frequencies of values to enable O(1) COUNT queries
        self.value_counts: Dict[Any, int] = {}
        
        # Transaction stack holding dictionaries that map key -> old_value (or NO_VALUE)
        self.transaction_stack: List[Dict[str, Any]] = []
        
        # First-Order Markov Chain Cache
        self.cache = PredictiveCache()

    def set(self, key: str, value: Any) -> None:
        """
        Sets the value of a key.
        Updates both the live database and value counts.
        Records the old value in the active transaction's undo log if applicable.
        """
        # If in a transaction, log the old state before mutating
        if self.transaction_stack:
            active_log = self.transaction_stack[-1]
            if key not in active_log:
                if key in self.db:
                    active_log[key] = self.db[key]
                else:
                    active_log[key] = NO_VALUE

        # Update value counts
        if key in self.db:
            old_value = self.db[key]
            self._decrement_value_count(old_value)

        self.db[key] = value
        self._increment_value_count(value)

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves the value of a key (returns None if not present).
        Records the read operation in the PredictiveCache.
        """
        # Telemetry: Record access to this key even if it doesn't exist
        self.cache.record_access(key)
        return self.db.get(key, None)

    def unset(self, key: str) -> None:
        """
        Removes a key from the database.
        Updates both the live database and value counts.
        Records the old value in the active transaction's undo log if applicable.
        """
        if key not in self.db:
            return

        # If in a transaction, log the old state before mutating
        if self.transaction_stack:
            active_log = self.transaction_stack[-1]
            if key not in active_log:
                active_log[key] = self.db[key]

        # Update value counts & remove key
        old_value = self.db[key]
        self._decrement_value_count(old_value)
        del self.db[key]

    def count(self, value: Any) -> int:
        """
        Returns the number of keys that currently hold the given value.
        Executes in O(1) time.
        """
        return self.value_counts.get(value, 0)

    def begin(self) -> None:
        """
        Starts a new transaction block. Nested transactions are pushed to the stack.
        """
        self.transaction_stack.append({})

    def commit(self) -> None:
        """
        Commits changes made in the current transaction block.
        If nested, merges the current transaction's undo log into the parent's log.
        If outermost, discards the log to make changes permanent.
        Raises ValueError if no active transaction exists.
        """
        if not self.transaction_stack:
            raise ValueError("NO ACTIVE TRANSACTION")

        # Pop the current transaction log
        active_log = self.transaction_stack.pop()

        # If there is a parent transaction, merge active_log into it
        if self.transaction_stack:
            parent_log = self.transaction_stack[-1]
            for key, original_val in active_log.items():
                # Crucial step: Only record the change in the parent transaction
                # if the parent transaction was not already tracking this key.
                # This ensures the parent preserves the value of the key from
                # before the parent transaction started.
                if key not in parent_log:
                    parent_log[key] = original_val

    def rollback(self) -> None:
        """
        Rolls back the current transaction, restoring database and value count state.
        Raises ValueError if no active transaction exists.
        """
        if not self.transaction_stack:
            raise ValueError("NO ACTIVE TRANSACTION")

        active_log = self.transaction_stack.pop()

        # Reverse the changes in active_log
        for key, old_value in active_log.items():
            if old_value is NO_VALUE:
                # Key did not exist before this transaction block; delete it if it does now
                if key in self.db:
                    current_val = self.db[key]
                    self._decrement_value_count(current_val)
                    del self.db[key]
            else:
                # Restore the key's original value
                if key in self.db:
                    current_val = self.db[key]
                    self._decrement_value_count(current_val)
                self.db[key] = old_value
                self._increment_value_count(old_value)

    def save_to_disk(self, filename="spreedb_snapshot.json") -> None:
        """Takes a snapshot of the current global state and saves it to disk."""
        if self.transaction_stack:
            print("[WARNING] You have uncommitted transactions! Only the global state will be saved.")
            
        try:
            # We save both the data AND the machine learning transition history!
            snapshot = {
                "db": self.db,
                "ml_transitions": self.cache.transitions
            }
            with open(filename, "w") as f:
                json.dump(snapshot, f, indent=4)
            print(f"[SAVED] Snapshot successfully saved to {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to save snapshot: {e}")

    def load_from_disk(self, filename="spreedb_snapshot.json") -> None:
        """Loads a snapshot from disk, replacing current state."""
        if not os.path.exists(filename):
            print(f"[ERROR] No snapshot found at {filename}")
            return
            
        try:
            with open(filename, "r") as f:
                snapshot = json.load(f)
                
            self.db = snapshot.get("db", {})
            self.cache.transitions = snapshot.get("ml_transitions", {})
            
            # Rebuild the O(1) value counts based on the loaded database
            self.value_counts.clear()
            for val in self.db.values():
                self.value_counts[val] = self.value_counts.get(val, 0) + 1
                
            # Clear active transactions to prevent state corruption
            self.transaction_stack.clear()
            
            # Reset cache sequence history to avoid leakage from previous session queries
            self.cache.last_key = None
            
            print(f"[LOADED] Snapshot successfully loaded from {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to load snapshot: {e}")

    def _increment_value_count(self, value: Any) -> None:
        self.value_counts[value] = self.value_counts.get(value, 0) + 1

    def _decrement_value_count(self, value: Any) -> None:
        if value in self.value_counts:
            self.value_counts[value] -= 1
            if self.value_counts[value] <= 0:
                del self.value_counts[value]


def print_help() -> None:
    print("\n\033[95mSupported SpreeDB Commands:\033[0m")
    print("  \033[1mSET <key> <value>\033[0m   - Sets the value for a key.")
    print("  \033[1mGET <key>\033[0m           - Retrieves the value of a key (triggers cache prefetch prediction).")
    print("  \033[1mUNSET <key>\033[0m         - Deletes a key.")
    print("  \033[1mCOUNT <value>\033[0m       - Returns the number of keys with the given value [O(1)].")
    print("  \033[1mBEGIN\033[0m               - Starts a new transaction block.")
    print("  \033[1mCOMMIT\033[0m              - Commits the current transaction block.")
    print("  \033[1mROLLBACK\033[0m            - Rolls back the current transaction block.")
    print("  \033[1mSAVE [filename]\033[0m     - Saves a snapshot of database and ML cache to disk.")
    print("  \033[1mLOAD [filename]\033[0m     - Loads a database snapshot from disk.")
    print("  \033[1mTELEMETRY\033[0m           - Prints the current Markov Chain transition matrix.")
    print("  \033[1mSTATE\033[0m               - Prints the internal DB state, value counts, and transaction stack.")
    print("  \033[1mHELP\033[0m                - Shows this help guide.")
    print("  \033[1mEXIT\033[0m                - Exits the SpreeDB shell.\n")


def main() -> None:
    db = SpreeDB()
    print("\033[94m" + "=" * 55 + "\033[0m")
    print("\033[1;32m   *** Welcome to SpreeDB — Interactive Database Shell ***\033[0m")
    print("\033[36m   Nested Transactions & Markov Chain Predictive Prefetch\033[0m")
    print("\033[94m" + "=" * 55 + "\033[0m")
    print("Type 'HELP' to see the list of supported commands.")

    while True:
        try:
            # Display active transaction nesting indicator in the prompt
            nesting_level = len(db.transaction_stack)
            prompt = f"\033[1;33m(txn:{nesting_level}) spreedb>\033[0m " if nesting_level > 0 else "\033[1;34mspreedb>\033[0m "
            
            line = input(prompt).strip()
            if not line:
                continue

            parts = line.split()
            cmd = parts[0].upper()

            if cmd == "EXIT":
                print("\033[93mExiting SpreeDB. Goodbye!\033[0m")
                break

            elif cmd == "HELP":
                print_help()

            elif cmd == "SET":
                if len(parts) < 3:
                    print("\033[91mUsage: SET <key> <value>\033[0m")
                    continue
                key = parts[1]
                # Join remaining parts as the value string
                val = " ".join(parts[2:])
                db.set(key, val)
                print(f"\033[32mOK\033[0m")

            elif cmd == "GET":
                if len(parts) != 2:
                    print("\033[91mUsage: GET <key>\033[0m")
                    continue
                key = parts[1]
                
                # Retrieve from database
                val = db.get(key)
                if val is None:
                    print("\033[90m(nil)\033[0m")
                else:
                    print(f"\033[1;37m{val}\033[0m")

                # Cache Prefetch Recommendation
                prediction = db.cache.predict(key)
                if prediction:
                    print(f"\033[95m[PREFETCH PREDICTION: Recommended next key is '{prediction}']\033[0m")

            elif cmd == "UNSET":
                if len(parts) != 2:
                    print("\033[91mUsage: UNSET <key>\033[0m")
                    continue
                key = parts[1]
                db.unset(key)
                print(f"\033[32mOK\033[0m")

            elif cmd == "COUNT":
                if len(parts) < 2:
                    print("\033[91mUsage: COUNT <value>\033[0m")
                    continue
                val = " ".join(parts[1:])
                c = db.count(val)
                print(f"\033[32m{c}\033[0m")

            elif cmd == "BEGIN":
                db.begin()
                print(f"\033[33mTransaction started (Level: {len(db.transaction_stack)})\033[0m")

            elif cmd == "COMMIT":
                try:
                    db.commit()
                    print(f"\033[32mCOMMIT SUCCESS\033[0m")
                except ValueError as e:
                    print(f"\033[91mERROR: {e}\033[0m")

            elif cmd == "ROLLBACK":
                try:
                    db.rollback()
                    print(f"\033[33mROLLBACK SUCCESS\033[0m")
                except ValueError as e:
                    print(f"\033[91mERROR: {e}\033[0m")

            elif cmd == "SAVE":
                db.save_to_disk()

            elif cmd == "LOAD":
                db.load_from_disk()

            elif cmd == "TELEMETRY":
                print(db.cache.format_telemetry())

            elif cmd == "STATE":
                print("\033[35m=== Internal DB State ===\033[0m")
                print(f"  \033[1mDatabase:\033[0m {db.db}")
                print(f"  \033[1mValue Frequencies:\033[0m {db.value_counts}")
                print(f"  \033[1mTransaction Stack (Undo Logs):\033[0m")
                if not db.transaction_stack:
                    print("    (Empty)")
                else:
                    for i, log in enumerate(db.transaction_stack):
                        readable_log = {k: ("NO_VALUE" if v is NO_VALUE else v) for k, v in log.items()}
                        print(f"    [{i}] -> {readable_log}")

            else:
                print(f"\033[91mUnknown command: {cmd}. Type HELP for command syntax.\033[0m")

        except KeyboardInterrupt:
            print("\n\033[93mUse EXIT to quit the shell.\033[0m")
        except Exception as e:
            print(f"\033[91mUnexpected System Error: {e}\033[0m")

if __name__ == "__main__":
    main()
