import readline

class Shell:
    __commands = None
    __cmdhelp = None
    __trace = None
    __prompt = None
    __exitcmds = None
 
    def __init__(self):
        self.__commands = {}
        self.__cmdhelp = {}
        self.setcmd('@!', self.poptrace, "- Pops last exception off trace stack")
        self.setcmd('@load', self.loadmodule, "<module> - Imports an extension")
        self.setcmd('@>', self.setprompt, "[string] - Sets interactive prompt to string, default if blank")
        self.setcmd('?', self.help, "- Displays help message")

        self.__trace = []
        self.__exitcmds = ['exit', 'quit']

        self.setprompt()

    def help(self, arg):
        if not arg:
            return "? <command> - Displays command help, if available\nAvailable commands: %s" % ", ".join(self.__commands.keys())    
        if (arg in self.__commands) and (arg in self.__cmdhelp) and (self.__cmdhelp[arg]):
            return "%s %s" % (arg, self.__cmdhelp[arg])
        if arg not in self.__commands:
            return "%s is unbound" % arg
        
        return "No help for %s" % arg

    def setcmd(self, keyword, fn, help=None):
        if keyword and not fn:
            del(__commands[keyword])
            del(__cmdhelp[keyword])
        if keyword and fn:
            self.__commands[keyword] = fn
            self.__cmdhelp[keyword] = help

    def setprompt(self, input=None):
        if input:
            self.__prompt = input
        else:
            self.__prompt = "> "

    def poptrace(self, input):
        if len(self.__trace) == 0:
            return "No exceptions on stack."
        else:
            return self.__trace.pop()

    def loadmodule(self, input):
        commands = []
        try:
            mod =__import__(input)
            if 'exports' in dir(mod):
                exportlist = mod.exports()
                for export in exportlist:
                    self.setcmd(export[1], export[2])
                    commands.append(export[1])
                msg = "%s new commands imported from %s [%s]" % (len(commands), mod.__name__, ','.join(commands))
                return msg 
            else:
                return "Could not enumerate module exports in %s" % mod.__name__
        except ImportError, e:
            return "Load failed, couldn't import %s" % input
 
    def completer(self, input, state):
        options = [c for c in self.__commands.keys() if c.startswith(input)]
        opt = None
        try:
            opt = options[state]
        except IndexError:
            opt = None
        return opt
 
    def handle(self, input):
        if not input:
            return
        try:
            (cmd, args) = input.split(' ', 1)
        except ValueError:
            cmd = input
            args = None

        if cmd in self.__commands.keys():
            try:
                return self.__commands[cmd](args)
            except AttributeError or NameError, e:
                print e
                self.__trace.append(e)
                return "Command '%s' failed" % cmd
            except TypeError, e:
                print e
                self.__trace.append(e)
                return "Bad argument '%s' for '%s'" % (args, cmd)
        else:
            return self.default(input)
 
    def default(self, input):
        return input
 
    def start(self, ret=None):
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")

        while True:
            try:
                input = raw_input(self.__prompt)
                
                if input in self.__exitcmds:
                    break
 
                result = self.handle(input)
                if result:
                    print result
                else:
                    print input
            except KeyboardInterrupt:
                break
        return ret
 
if __name__ == "__main__":
    s = Shell()
    import calc

    def subshell(arg):
        ss = Shell()
        ss.prompt = "subshell> "
        ss.setcmd('hex', lambda x: "0x%x" % int(x))
        ss.start("Subshell")

    s.setcmd('sqr', lambda x: int(x) * int(x), "<x> - Returns x*x")
    s.setcmd('subshell', subshell)
    s.setcmd('calc', calc.Calc)
    s.setprompt('test> ')
    s.start()

