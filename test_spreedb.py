import unittest
import os
from spreedb import SpreeDB, PredictiveCache, NO_VALUE

class TestSpreeDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = SpreeDB()

    def test_basic_operations(self) -> None:
        """Tests standard SET, GET, UNSET, and COUNT functionality."""
        # Initial empty state
        self.assertIsNone(self.db.get("a"))
        self.assertEqual(self.db.count("10"), 0)

        # SET and GET
        self.db.set("a", "10")
        self.assertEqual(self.db.get("a"), "10")
        self.assertEqual(self.db.count("10"), 1)

        # Update value
        self.db.set("a", "20")
        self.assertEqual(self.db.get("a"), "20")
        self.assertEqual(self.db.count("10"), 0)
        self.assertEqual(self.db.count("20"), 1)

        # Multiple keys with same value
        self.db.set("b", "20")
        self.assertEqual(self.db.count("20"), 2)

        # UNSET
        self.db.unset("a")
        self.assertIsNone(self.db.get("a"))
        self.assertEqual(self.db.count("20"), 1)

        # UNSET non-existent key
        self.db.unset("non_existent")
        self.assertEqual(self.db.count("20"), 1)

    def test_basic_transactions_rollback(self) -> None:
        """Tests a single transaction level block rolling back to original state."""
        self.db.set("a", "10")
        self.db.set("b", "20")

        self.db.begin()
        self.db.set("a", "99")
        self.db.unset("b")
        self.db.set("c", "30")

        # In-transaction state
        self.assertEqual(self.db.get("a"), "99")
        self.assertIsNone(self.db.get("b"))
        self.assertEqual(self.db.get("c"), "30")
        self.assertEqual(self.db.count("99"), 1)
        self.assertEqual(self.db.count("20"), 0)
        self.assertEqual(self.db.count("30"), 1)

        # Rollback
        self.db.rollback()

        # Reverted state
        self.assertEqual(self.db.get("a"), "10")
        self.assertEqual(self.db.get("b"), "20")
        self.assertIsNone(self.db.get("c"))
        self.assertEqual(self.db.count("10"), 1)
        self.assertEqual(self.db.count("20"), 1)
        self.assertEqual(self.db.count("30"), 0)

    def test_basic_transactions_commit(self) -> None:
        """Tests a single transaction level block committing permanently."""
        self.db.set("a", "10")
        
        self.db.begin()
        self.db.set("a", "20")
        self.db.set("b", "30")
        self.db.commit()

        # Committed state persists
        self.assertEqual(self.db.get("a"), "20")
        self.assertEqual(self.db.get("b"), "30")
        self.assertEqual(self.db.count("20"), 1)
        self.assertEqual(self.db.count("30"), 1)

        # Trying to rollback raises error
        with self.assertRaises(ValueError):
            self.db.rollback()

    def test_nested_transactions_rollback(self) -> None:
        """Tests that rolling back a nested transaction leaves the outer transaction active."""
        self.db.set("a", "10")

        # Outer transaction
        self.db.begin()
        self.db.set("a", "20")

        # Nested transaction
        self.db.begin()
        self.db.set("a", "30")
        self.assertEqual(self.db.get("a"), "30")
        
        # Rollback nested transaction
        self.db.rollback()
        
        # Should return to outer transaction state
        self.assertEqual(self.db.get("a"), "20")
        self.assertEqual(len(self.db.transaction_stack), 1)

        # Rollback outer transaction
        self.db.rollback()
        
        # Should return to original state
        self.assertEqual(self.db.get("a"), "10")
        self.assertEqual(len(self.db.transaction_stack), 0)

    def test_nested_transactions_commit_and_outer_rollback(self) -> None:
        """Tests that a nested commit merges changes, but an outer rollback still reverts them all."""
        self.db.set("a", "10")

        # Outer transaction
        self.db.begin()
        self.db.set("a", "20")

        # Nested transaction
        self.db.begin()
        self.db.set("a", "30")
        self.db.set("b", "40")
        
        # Commit nested
        self.db.commit()
        
        # Current active state (nested committed, but outer still active)
        self.assertEqual(self.db.get("a"), "30")
        self.assertEqual(self.db.get("b"), "40")
        self.assertEqual(len(self.db.transaction_stack), 1)

        # Rollback outer transaction (should undo everything, including the nested changes!)
        self.db.rollback()

        # All changes reverted to pre-outer state
        self.assertEqual(self.db.get("a"), "10")
        self.assertIsNone(self.db.get("b"))
        self.assertEqual(len(self.db.transaction_stack), 0)

    def test_nested_transactions_double_commit(self) -> None:
        """Tests nested commits cascading up to permanent database updates."""
        self.db.set("a", "10")

        self.db.begin()
        self.db.set("a", "20")

        self.db.begin()
        self.db.set("b", "30")
        self.db.commit() # Nested commit merges into outer

        self.db.commit() # Outer commit writes to database permanently

        self.assertEqual(self.db.get("a"), "20")
        self.assertEqual(self.db.get("b"), "30")
        self.assertEqual(len(self.db.transaction_stack), 0)

    def test_transaction_errors(self) -> None:
        """Tests that committing or rolling back without active transactions raises ValueError."""
        with self.assertRaises(ValueError):
            self.db.commit()
            
        with self.assertRaises(ValueError):
            self.db.rollback()

    def test_predictive_cache_transitions(self) -> None:
        """Tests that the PredictiveCache accurately captures state transitions and tie-breaks."""
        cache = PredictiveCache()
        
        # Record transitions: A -> B, A -> B, A -> C
        cache.record_access("A")
        cache.record_access("B")  # A -> B (count 1)
        cache.record_access("A")  # B -> A (count 1)
        cache.record_access("B")  # A -> B (count 2)
        cache.record_access("A")  # B -> A (count 2)
        cache.record_access("C")  # A -> C (count 1)

        # Transition matrix inspection:
        # A exited to B twice, C once. Prediction for A should be B.
        self.assertEqual(cache.predict("A"), "B")

        # B exited to A twice. Prediction for B should be A.
        self.assertEqual(cache.predict("B"), "A")

        # C has no transitions from it yet. Prediction for C should be None.
        self.assertIsNone(cache.predict("C"))

        # Test deterministic alphabetical tie-breaking
        # Clear transitions or create new cache
        tie_cache = PredictiveCache()
        # Transitions: X -> Z (count 1), X -> Y (count 1)
        tie_cache.record_access("X")
        tie_cache.record_access("Z")
        tie_cache.record_access("X")
        tie_cache.record_access("Y")

        # Count of X -> Z is 1, X -> Y is 1. Alphabetical first is Y.
        self.assertEqual(tie_cache.predict("X"), "Y")

    def test_snapshot_persistence(self) -> None:
        """Tests that SpreeDB state and ML transitions can be saved to and loaded from disk."""
        import os
        filename = "test_snapshot.json"
        if os.path.exists(filename):
            os.remove(filename)

        # Set up initial state with both data and ML cache transitions
        self.db.set("name", "Alice")
        self.db.set("role", "Engineer")
        self.db.get("name")
        self.db.get("role")  # Transition name -> role

        # Save to disk
        self.db.save_to_disk(filename)
        self.assertTrue(os.path.exists(filename))

        # Create a new blank database instance
        new_db = SpreeDB()
        self.assertIsNone(new_db.get("name"))
        self.assertEqual(new_db.count("Alice"), 0)

        # Load from disk
        new_db.load_from_disk(filename)
        self.assertEqual(new_db.get("name"), "Alice")
        self.assertEqual(new_db.get("role"), "Engineer")
        self.assertEqual(new_db.count("Alice"), 1)
        self.assertEqual(new_db.count("Engineer"), 1)

        # Confirm transitions loaded and prediction works
        self.assertEqual(new_db.cache.predict("name"), "role")

        # Clean up test snapshot file
        if os.path.exists(filename):
            os.remove(filename)

    def test_persistence(self):
        """Verifies that state and ML history survive a save/load cycle."""
        test_file = "test_snapshot.json"
        
        # 1. Establish the initial state and train the cache
        self.db.set("hero", "Batman")
        self.db.get("hero")
        self.db.get("villain") # Teaches the Markov Chain: hero -> villain
        
        # Save to disk
        self.db.save_to_disk(test_file)
        
        # 2. Simulate a complete system reboot by creating a fresh instance
        rebooted_db = SpreeDB()
        
        # Before loading, it should be empty
        self.assertIsNone(rebooted_db.get("hero"))
        
        # 3. Re-hydrate from disk
        rebooted_db.load_from_disk(test_file)
        
        # 4. Assert data and index integrity
        self.assertEqual(rebooted_db.get("hero"), "Batman")
        self.assertEqual(rebooted_db.count("Batman"), 1) # O(1) index rebuilt!
        
        # Assert ML Cache survived
        self.assertEqual(rebooted_db.cache.predict_next("hero"), "villain")
        
        # Clean up the test file so we don't clutter the workspace
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    unittest.main()
