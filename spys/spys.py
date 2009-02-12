import readline

class SPyShell(object):
    """
    Simple Python Shell (SPyS) implements an interactive, functional shell/REPL* extensible using a
    dynamically loading plugin architecture. [REPL = read-eval-print loop]
    
    Invocation of a new SPyS instance is accomplished by creating a new SPyS instance and calling 
    the start() method. On invocation, SPyS will start up an interactive command shell that provides
    a few utility functions:
        @load <module> - Dynamically load <module>, importing provided commands into the SPyS environment
        @! - If a command fails, @! will print the thrown exception, useful for debugging
        @> [string] - Sets command shell prompt to [string], resets prompt to default if called with no argument
        @exec <string> - Executes python statement <string> in the current execution context
        @bind <keyword> <string> - Binds python function definiton in <string> to <keyword>
        ? [cmd]- Displays help message
    
    In addition to dynamic plugin loading, callable objects can be bound to keywords in a SPyS instance via
    the setcmd method. Functions called by SPyS will be passed a single argument consisting of all 
    characters following the command executed on the SPyS command line. All parsing of command arguments 
    is handled by the called function.

    For example, to bind a command "hex" that implements a simple dec->hex converter:
        spysinstance.setcmd('hex', lambda x:"%x" % int(x))
    This can also be done from within the SPyS instance REPL, using self:
        @exec self.setcmd('hex', lambda x:"%x" % int(x))
    SPyS also provides a shortcut in the REPL for binding inlined functions:
        @bind hex lambda x:"%x" % int(x)

    Previously bound commands can be removed by passing None instead of a function to setcmd.

    By default, any input that does not match a bound command is passed to the default(arg) method,
    which can be overridden to provide custom input handling.

    """
    def __init__(self, arg=None):
        self.__commands = {}
        self.__cmdhelp = {}
        self.setcmd('@!', self.poptrace, "- Pops last exception off trace stack")
        self.setcmd('@load', self.loadmodule, "<module> - Imports an extension")
        self.setcmd('@>', self.setprompt, "[string] - Sets interactive prompt to string, default if blank")
        self.setcmd('?', self.help, "- Displays help message")
        self.setcmd('@exec', self.execute, "<statement> - Execute a python statement")
        self.setcmd('@bind', self.bindfn, "<keyword> <string> - Bind inlined function in <string> to <keyword>")
        self.__trace = []
        self.__exitcmds = ['exit', 'quit']

        self.setprompt()

    def help(self, arg):
        if not arg:
            return "? <command> - Displays command help, if available\nAvailable commands: %s" % ", ".join(sorted(self.__commands.keys()))    
        if (arg in self.__commands) and (arg in self.__cmdhelp) and (self.__cmdhelp[arg]):
            return "%s %s" % (arg, self.__cmdhelp[arg])
        if arg not in self.__commands:
            return "%s is unbound" % arg
        
        return "No help for %s" % arg
    
    def setcmd(self, keyword, fn, help=None):
        if keyword and not fn:
            del(self.__commands[keyword])
            del(self.__cmdhelp[keyword])
        if keyword and fn:
            self.__commands[keyword] = fn
            self.__cmdhelp[keyword] = help

    def setprompt(self, input=None):
        if input:
            self.__prompt = input
        else:
            self.__prompt = "spys> "

    def poptrace(self, input):
        if len(self.__trace) == 0:
            return "No exceptions on stack."
        else:
            return self.__trace.pop()
    
    def execute(self, input):
        try:
            exec input
        except Exception, e:
            self.__trace.append(e)
            return "Execution failed"

    def bindfn(self, input):
        (keyword, fn) = input.split(' ', 1)
        expr = "self.setcmd('%s', %s, '''(bound function <<%s>>)''')" % (keyword, fn, fn)
        try:
            exec expr
            return "<<%s>> bound to '%s'" % (fn, keyword)
        except Exception, e:
            self.__trace.append(e)
            return "Bind failed"

    def loadmodule(self, input):
        commands = []
        try:
            mod =__import__(input)
            if 'spys_exports' in dir(mod):
                exportlist = mod.spys_exports()
                for export in exportlist:
                    self.setcmd(export[1], export[2])
                    commands.append(export[1])
                msg = "%s new commands imported from %s (%s)" % (len(commands), mod.__name__, ', '.join(commands))
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
                self.__trace.append(e)
                return "Command '%s' failed" % cmd
            except TypeError, e:
                self.__trace.append(e)
                return "Bad argument '%s' for '%s'" % (args, cmd)
        else:
            return self.default(input)
 
    def default(self, input):
        pass
 
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

            except KeyboardInterrupt:
                break
        return ret
 
if __name__ == "__main__":
    s = SPyShell()

    def subshell(arg):
        ss = SPyShell()
        ss.prompt = "subshell> "
        ss.setcmd('hex', lambda x: "0x%x" % int(x))
        ss.start("Subshell")

    s.setcmd('sqr', lambda x: int(x) * int(x), "<x> - Returns x*x")
    s.setcmd('subshell', subshell)
    s.start()

