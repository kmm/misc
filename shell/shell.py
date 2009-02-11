import readline

class Shell:
    commands = {}
    trace = [] 

    prompt = "> "
    exitcmd = "exit"

    def __init__(self):
        self.commands['test'] = self.default
        self.commands['!'] = self.poptrace

    def poptrace(self, input):
        if len(self.trace) == 0:
            return "No exceptions on stack."
        else:
            return self.trace.pop()

    def completer(self, input, state):
        options = [cmd for cmd in self.commands.keys() if cmd.startswith(input)]
        try:
            return options[state]
        except IndexError:
            return None

    def handle(self, input):
        if not input:
            return

        try:
            (cmd, args) = input.split(' ', 1)
        except ValueError:
            cmd = input
            args = None

        if cmd in self.commands.keys():
            try:
                return self.commands[cmd](args)
            except AttributeError or NameError, e:
                # lists have pop() but no push()! wtf?
                self.trace.insert(0, e)
                return "Unknown command '%s'" % cmd
            except TypeError, e:
                self.trace.insert(0, e)
                return "Bad argument '%s' for '%s'" % (args, cmd)
        else:
            return self.default(input)

    def default(self, input):
        return input

    def start(self):
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")

        while True:
            input = raw_input(self.prompt)

            if input == self.exitcmd:
                break

            result = self.handle(input)            
            if result:
                print result
            else:
                print input
        
        return True

s = Shell()

def subshell(parent):
    ss = Shell()
    ss.prompt = "subshell> "
    ss.exitcmd = "z"
    return ss.start()

s.commands['sqr'] = lambda x: int(x) ** int(x)
s.commands['subshell'] = subshell
s.start()
