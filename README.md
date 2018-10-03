# redisnot

Borat's favorite Python clone of redis. A key-value store ("data structures server") written mainly to explore how redis is designed and implemented. In certain places, I depart from how redis does things.

## Next Steps

- Redis protocol (de)serializer
- AOF persistence scheme
- More commands for strings.py and keys.py
- Test suite (unit, integration)
- Per-key write locks
- Maxmemory + disk BTree swapping
- Reloading with AOF/RDB
- Benchmarks
- How can we reason about atomicity, consistency, isolation, durability?
- Cluster mode??

## Desired Features
- Redis Protocol (GET, SET, etc)
- Abstract Data Types (Strings, Lists, Sets, Hashes, Sorted Sets)
- Tunable In-Memory Storage (beyond a specified size, will swap to disk. default: 1GB)
- Data Persistence ("RDB"-ish B-Tree, or "AOF", or both)
- Preloaded Data (provide an RDB or AOF file to seed on startup)
- CLI tool
- TBD: cluster? sentinel?

## Getting Started

First, install any necessary Python packages. Using virtualenv is recommended to keep packages clean:
```bash
# assuming your pwd is redisnot
virtualenv env
source env/bin/activate
(env) pip install -r requirements.txt
```

Next, in one shell, start up the server:
```bash
# by default listening on port 6379
./db/server.py
```

--TODO: Not implemented yet--

Then, in a different shell, start up the CLI tool:
```bash
./db/tool.py
```

Try PING-ing the server from the CLI tool:
```bash
$ PING
# should respond PONG
```

--TODO: test suite--

# Server Options

TODO: enumerate server options, with examples

# Commands Supported

TODO: enumerate commands supported, with examples

# Abstract Data Types Supported

TODO: enumerate ADTs supported

# Notes

TODO: include some notes and links to resources conferred
