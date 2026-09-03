# ⚡ SpreeDB

> A Python-based in-memory key-value database featuring nested transactions, O(1) value counting, Markov-chain predictive caching, JSON persistence, and multithreaded TCP client-server support.

---

## 🚀 Live Demo

👉 [Open SkillSpree Dashboard](https://skillspree-learning-platform-de67sz2ggmvvhdrdkttfxm.streamlit.app/)

---

## 🚀 Overview

SpreeDB is a lightweight database engine built from scratch in Python.

The project demonstrates fundamental database and systems concepts including:

- In-memory key-value storage
- O(1) value frequency counting
- Nested transactions
- Commit and rollback operations
- Undo-log based transaction management
- First-order Markov Chain predictive caching
- JSON snapshot persistence
- Multithreaded TCP server support
- Automated unit testing

The goal of SpreeDB is to explore how database engines manage state, transactions, indexing, persistence, and client-server communication.

---

# ✨ Features

## 🗄️ Key-Value Storage

SpreeDB supports standard database operations:

```text
SET <key> <value>
GET <key>
UNSET <key>

Example:

SET name Alice
GET name

Output:
Alice
⚡ O(1) COUNT Queries

SpreeDB maintains an internal value frequency index.

This allows the database to count how many keys contain a particular value in constant time.

Example:

SET alice developer
SET bob developer

COUNT developer

Output:
2

Internally:

value_counts[value] = frequency
🔄 Nested Transactions

SpreeDB supports multiple levels of transactions.

Example:

BEGIN
SET a 10

BEGIN
SET a 20

ROLLBACK

After rolling back the nested transaction:

a = 10

Supported transaction commands:

BEGIN
COMMIT
ROLLBACK

Transactions use undo logs to restore previous database states.

🧠 Markov Chain Predictive Cache

SpreeDB tracks sequential GET operations.

For example:

GET A
GET B

GET A
GET B

GET A
GET C

The system learns transitions:

A → B : 2
A → C : 1

The predictive cache uses a First-Order Markov Chain.

When transition frequencies are equal, alphabetical ordering provides deterministic tie-breaking.

💾 JSON Persistence

SpreeDB can save the current database state and predictive cache transitions.

SAVE

The snapshot stores:

Database values
Markov Chain transitions

Example snapshot:

{
    "db": {
        "alice": "developer"
    },
    "ml_transitions": {
        "alice": {
            "bob": 2
        }
    }
}

Load a previous snapshot:

LOAD
🌐 Multithreaded TCP Server

SpreeDB includes a TCP server capable of handling multiple clients.

Each connected client is processed using a separate thread.

Architecture:

                ┌───────────────┐
                │    Client 1   │
                └───────┬───────┘
                        │
                ┌───────▼───────┐
                │               │
                │ SpreeDB TCP   │
                │    Server     │
                │               │
                └───────┬───────┘
                        │
              ┌─────────▼─────────┐
              │                   │
              │   SpreeDB Engine  │
              │                   │
              └───────────────────┘
                        ▲
                        │
                ┌───────┴───────┐
                │    Client 2   │
                └───────────────┘

Supported network commands include:

SET
GET
SAVE
EXIT
🏗️ Project Structure
skillspree-learning-platform/
│
├── client.py
│   └── TCP client implementation
│
├── demo.py
│   └── Demonstrates database features
│
├── run_clients_demo.py
│   └── Runs multiple client demonstrations
│
├── server.py
│   └── Multithreaded TCP server
│
├── spreedb.py
│   └── Core database engine and CLI
│
├── spreedb_snapshot.json
│   └── Database snapshot
│
└── test_spreedb.py
    └── Automated unit tests
⚙️ Installation

Clone the repository:

git clone https://github.com/adityapandereio6-sketch/skillspree-learning-platform.git

Navigate into the project:

cd skillspree-learning-platform

No external Python packages are required.

▶️ Running SpreeDB

Start the interactive database shell:

python spreedb.py

Example:

*** Welcome to SpreeDB — Interactive Database Shell ***

spreedb> SET name Alice
OK

spreedb> GET name
Alice

spreedb> COUNT Alice
1
📚 Supported Commands
Command	Description
SET <key> <value>	Stores a value
GET <key>	Retrieves a value
UNSET <key>	Deletes a key
COUNT <value>	Counts matching values in O(1)
BEGIN	Starts a transaction
COMMIT	Commits the transaction
ROLLBACK	Restores the previous state
SAVE	Saves a database snapshot
LOAD	Loads a snapshot
TELEMETRY	Displays Markov Chain transitions
STATE	Displays internal database state
HELP	Displays available commands
EXIT	Exits the shell
🧪 Running Tests

Run the automated test suite:

python -m unittest test_spreedb.py

The tests verify:

Basic SET, GET and UNSET operations
O(1) COUNT functionality
Transaction rollback
Transaction commit
Nested transactions
Nested commit and rollback behavior
Transaction error handling
Markov Chain transitions
Deterministic prediction tie-breaking
JSON persistence
🎯 Demonstration

Run the feature demonstration:

python demo.py

The demonstration covers:

Basic key-value operations
O(1) value frequency counting
Nested transactions
Commit and rollback
Markov Chain predictive caching
Transition telemetry
JSON snapshot persistence
🧠 Core Architecture
                  ┌─────────────────────┐
                  │   Interactive CLI   │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │      SpreeDB        │
                  │    Core Engine      │
                  └──────┬───────┬──────┘
                         │       │
             ┌───────────▼───┐ ┌─▼──────────────┐
             │ In-Memory DB  │ │ Value Frequency │
             │ Dictionary    │ │ Index O(1)      │
             └───────────────┘ └────────────────┘
                         │
             ┌───────────▼───────────┐
             │ Transaction Undo Logs │
             │   Nested Transactions │
             └───────────────────────┘
                         │
             ┌───────────▼───────────┐
             │ Predictive Cache      │
             │ First-Order Markov    │
             │ Chain                 │
             └───────────────────────┘
                         │
             ┌───────────▼───────────┐
             │ JSON Persistence      │
             └───────────────────────┘
🛠️ Technologies Used
Python
Dictionaries and Hash Maps
JSON Serialization
Socket Programming
Multithreading
Unit Testing
First-Order Markov Chains
📈 Key Engineering Concepts

This project demonstrates practical implementation of:

Database state management
Hash-based indexing
Transaction processing
Undo logging
Nested transactions
Predictive caching
Sequential access pattern analysis
TCP networking
Concurrent client handling
Data persistence
Automated testing
👨‍💻 Author

Aditya Pandere

B.Tech Computer Science Engineering (AI & ML)

GitHub: https://github.com/adityapandereio6-sketch

⭐ If you found this project interesting, consider giving the repository a star!
