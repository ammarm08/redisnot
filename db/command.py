
class Command(object):
    
    def __init__(self, name, func, opts):
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
