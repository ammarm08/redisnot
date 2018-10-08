# redisnot

Borat's favorite Python clone of redis. A key-value store ("data structures server") written mainly to explore how redis is designed and implemented. In certain places, I depart from how redis does things.

Currently supports getting and setting of strings, as well as AOF log-based persistence.

## Next Steps

- Redis protocol (de)serializer
- More command coverage
- More test coverage
- RDB as a persistence strategy
- CLI client
- Benchmarks
- How can we reason about atomicity, consistency, isolation, durability?
- Cluster mode??


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
# by default listening on port 6379.
# add flag --help or -h to see configurable opts
python db/server.py
```


Then, in a different shell, open up `nc`:
```bash
nc localhost 6379
```

Try setting and getting some things:
```
> set foo bar
$ 'OK'
> get foo
$ 'bar'
```

# Tests

Currently minimal test coverage. To run tests:

```bash
nosetests -v
```

# Server Options

TODO: enumerate server options, with examples

# Commands Supported

TODO: enumerate commands supported, with examples

# Abstract Data Types Supported

TODO: enumerate ADTs supported

# Notes

TODO: include some notes and links to resources conferred
