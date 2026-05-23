import time
from spreedb import SpreeDB

def print_separator(title: str) -> None:
    print("\n" + "\033[94m" + "=" * 65 + "\033[0m")
    print(f"\033[1;36m>>> {title} <<<\033[0m")
    print("\033[94m" + "=" * 65 + "\033[0m")

def main() -> None:
    db = SpreeDB()

    # ==========================================
    # 1. Basic Key-Value Operations & O(1) COUNT
    # ==========================================
    print_separator("1. Basic Operations & O(1) Value Frequencies")
    
    print("Action: Setting keys 'alice' and 'bob' to 'developer'...")
    db.set("alice", "developer")
    db.set("bob", "developer")
    print(f"-> Alice: {db.get('alice')}")
    print(f"-> Bob: {db.get('bob')}")
    
    print("\nAction: Counting occurrences of value 'developer' (O(1) operation)...")
    print(f"-> Count of 'developer': {db.count('developer')}")

    print("\nAction: Re-setting 'alice' to 'manager'...")
    db.set("alice", "manager")
    print(f"-> Alice: {db.get('alice')}")
    print(f"-> Count of 'developer': {db.count('developer')}")
    print(f"-> Count of 'manager': {db.count('manager')}")

    # ==========================================
    # 2. Nested Transactions & Undo Logs
    # ==========================================
    print_separator("2. Nested Transactions with Memory-Efficient Undo Logs")

    print("Initial active state before transactions:")
    print(f"-> Alice: {db.get('alice')} | Bob: {db.get('bob')}")

    print("\nAction: BEGIN Transaction (Level 1)")
    db.begin()
    db.set("alice", "director")
    db.set("charlie", "intern")
    print(f"-> [Txn Level 1] Alice: {db.get('alice')} | Charlie: {db.get('charlie')}")

    print("\nAction: BEGIN Nested Transaction (Level 2)")
    db.begin()
    db.set("alice", "VP")
    db.unset("bob")
    print(f"-> [Txn Level 2] Alice: {db.get('alice')} | Bob: {db.get('bob')} (should be None)")

    print("\nAction: ROLLBACK Level 2 (Nested Transaction)")
    db.rollback()
    print("-> State reverted back to Txn Level 1:")
    print(f"-> Alice: {db.get('alice')} (should be director) | Bob: {db.get('bob')} (should be developer)")

    print("\nAction: COMMIT Level 1 Transaction to main database")
    db.commit()
    print("-> Current database state after Level 1 Commit:")
    print(f"-> Alice: {db.get('alice')} (should be director)")
    print(f"-> Charlie: {db.get('charlie')} (should be intern)")

    # ==========================================
    # 3. Markov Chain Predictive Caching
    # ==========================================
    print_separator("3. First-Order Markov Chain Cache Prefetching")
    
    print("Scenario: A user repeatedly retrieves keys in sequence.")
    print("Accessing sequences: A -> B, A -> B, A -> C\n")
    
    # Sequence 1: A -> B
    print("GET A...")
    db.get("A")
    print("GET B...")
    db.get("B")
    
    # Sequence 2: A -> B
    print("GET A...")
    db.get("A")
    print("GET B...")
    db.get("B")

    # Sequence 3: A -> C
    print("GET A...")
    db.get("A")
    print("GET C...")
    db.get("C")

    print("\nAction: Querying key 'A' again to check prefetch prediction...")
    print("GET A...")
    db.get("A")
    prediction = db.cache.predict("A")
    print(f"\033[95m-> [PREFETCH PREDICTION]: Next recommended key is '{prediction}' (expected 'B' due to higher frequency)\033[0m")

    print("\nAction: Displaying Markov Chain Transition Telemetry Matrix:")
    print(db.cache.format_telemetry())

    # ==========================================
    # 4. JSON Snapshot Serialization & Persistence
    # ==========================================
    print_separator("4. JSON Snapshot Persistence (Save/Load)")

    print("Action: Saving database snapshot to disk as 'demo_snapshot.json'...")
    db.save_to_disk("demo_snapshot.json")

    print("\nAction: Mutating active DB state by adding 'temp_key' and clearing old keys...")
    db.set("temp_key", "temporary_value")
    db.unset("Alice")
    db.unset("A")
    print(f"-> Active Database State: {db.db}")

    print("\nAction: Re-loading the snapshot 'demo_snapshot.json' from disk...")
    db.load_from_disk("demo_snapshot.json")
    print("-> State successfully restored from JSON:")
    print(f"-> Alice: {db.get('alice')} (should be director)")
    print(f"-> A: {db.get('A')} (should be nil/None)")
    print(f"-> temp_key: {db.get('temp_key')} (should be nil/None since it wasn't in snapshot)")
    
    # Clean up file
    import os
    if os.path.exists("demo_snapshot.json"):
        os.remove("demo_snapshot.json")


if __name__ == "__main__":
    main()
