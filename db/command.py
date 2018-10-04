
class Command(object):

    def __init__(self, name, func, opts):
        """
        Initializes a Command, which holds state about a
        redis command, such as its name, which function it
        should call to execute, and any other options relevant
        to the command's execution.

        "r" -> read
        "w" -> write
        "+" -> log to aof file
        """
        self.read = False
        self.write = False
        self.aof = False

        self.name = name
        self.func = func

        for opt in opts:
            if opt == '+':
                self.aof = True
            elif opt == 'r':
                self.read = True
            elif opt == 'w':
                self.write = True
