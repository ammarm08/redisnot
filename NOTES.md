STRUCTS:

redisServer
  - mainthread
  - port
  - fd (socket)
  - db

server.c

main()
- admin stuff
  - set locale and timezone, parse time of day into timeval struct
  - set oom handler based on malloc lib in use
  - srand(time(NULL)^getpid()) ??
  - set seed for hashing function
- initServerConfig
  - pthread_mutex_init (next client id, lruclock, unixtime)
  - updateCachedTime()
  - null byte for server's runid (why?)
  - changeReplicationId() and clearReplicationId2() (why?)
  - sets a bunch of server properties based on defaults or user specifications
  - getLRUClock() and atomicSet this to server's lruclock (why?)
  - resetServerSaveParams() then set server to save 10000ch/1m, 100ch/5m, 1ch/1h
  - replication related settings
  - set client output buffer limits
  - initialize commands table associated with server
  - other stuff -- monitoring, debugging, logging, Lua script settings
- sets up redis modules
- store executable path + args in safe place for future restart
- initSentinelConfig(), initSentinel if sentinel_mode
- check if in rdb/aof mode
- argparsing special cases
  - v/version
  - h/help
  - test-memory
- argparsing first arg is config file name
- argparsing regular cases (--option value --option value --option value)
- more sentinel specific stuff
- reads redis.conf and loads conf into server struct
- daemonize if user specified and !supervised
- initServer()
  - setupSignalHandlers()
  - set up main server properties: hz, pid, current_client, clients, etc
  - set up shared objects
  - adjust open fds limit (reserves some for persistence work)
  - creates event loop instance and unpacks it into server.el!
  - allocates space for num_dbs * server.db! (redisDb instance)
  - open up tcp listening socket
- createPidFile() if background or user-specified
- check if server's # of allowable queued listeners < kernel's somaxconn
- if not in sentinel mode
  - moduleLoadFromQueue
  - loadDataFromDisk
  - verifyClusterConfigWithData if in cluster mode
  - ipfd and sofd ??
- maxmemory setting check (<1mb => whoa what you doing?)
- setBeforeSleep, setAfterSleep
- MAIN EVENT LOOP RUNS
  - while the eventloop.stop boolean is false...
    - run beforesleep() if not null
      - stuff
    - aeProcessEvents => doesnt EXECUTE the events. just FIRES them.
      - no time_events or file_events? return
      - aeApiPoll() -> calls multiplexing API like libuv to gather events. depending on os, uses epoll or select
      - sets the after sleep callback now that we know we have things to aeProcess
      - iterate over collected events. for each:
        - do some logging on event stats/settings/status
        - associate event and it's index with the event loops open fds ("fired")
        - usually, redis will always exec readables before writables
        - rfileProc/wfileProc => two types of events -- read or write.

- delete event loop and then return 0





COMPONENTS:

- server
- event loop
- clients
- networking
- protoparser
- command execution
- abstract data types

0: operations on abstract data types namespaced by keys
  - implement an in-memory key-value store
  - create space for extension w/ more ADTs
  - create space for multiple databases, abstract out the implementation
1: basic networking implementing redis protocol
  - implement a tcp server and proto parser
  - create space for concurrent clients and reusing socket conns
2: client
  - implement a tcp client/repl that parses a statement and converts it into redis protocol to send over the wire
3: event loop
  - TBD
4: persistence
  - TBD


* Server will use asyncore to accept tcp messages
* Server will pass off message to Client
    - properties: command, other useful flags on status
    - READ:
      - unpack message (JSON equiv for redis protocol)
      - handle file_event (read, write to store)
      - handle error case
    - WRITE:
      - write back response to socket
* Server has a database
* Database has an in-memory component and on-disk component
* Command implements the abstract data types
