import inspect, traceback, types

class FixedStack(object):
    def __init__(self, size):
        self.size = size
        self.buffer = [None for x in range(0, size)]

    def __getitem__(self, key):
        return self.buffer[key]

    def __len__(self):
        return len(self.buffer)

    def items(self):
        return self.buffer
    
    def append(self, value):
        del(self.buffer[0])
        self.buffer.append(value)

    def pop(self):
        self.buffer.insert(0, None)
        return self.buffer.pop()

    def top(self):
        return self.buffer[-1]

class SPyIO(object):
    """
    SPyIO provides I/O abstraction and a shared dict to SPyShell instances via
    inheritance. By default, provides two I/O endpoints, out:0 and in:0, 
    which just wrap print and raw_input. Additional endpoints can be defined 
    using the registerinput() and registeroutput() methods. If a nonexistant
    endpoint is requested, the default handler will be used.
    Endpoints are just functions! See cursesdemo for an example of this and 
    why it's useful.
    """
    def __init__(self, arg=None):
        self.shared = {}
        self._outendpoints = {0:self.defaultoutput}
        self._inendpoints = {0:self.defaultinput}        

    def defaultoutput(self, data=None):
        print data
        return True
        
    def defaultinput(self, data=None):
        if data:
            indata = raw_input(data)
        else:
            indata = raw_input()
        return indata

    def output(self, data=None, endpoint=None):
        if not endpoint:
            self._outendpoints[0](data)
        elif (endpoint in self._outendpoints) and callable(self._outendpoints[endpoint]):
            self._outendpoints[endpoint](data)
        else:
            self._outendpoints[0](data)
    
    def input(self, data, endpoint=None):
        if not endpoint:
            return self._inendpoints[0](data)
        elif (endpoint in self._inendpoints) and callable(self._inendpoints[endpoint]):
            return self._inendpoints[endpoint](data)
        else:
            return self._inendpoints[0](data)

    def registeroutput(self, name, function):
        if callable(function):
            self._outendpoints[name] = function
        else:
            self._outendpoints[name] = defaultoutput
            return False

    def registerinput(self, name, function):
        if callable(function):
            self._inendpoints[name] = function
        else:
            self._inendpoints[name] = defaultinput
            return False

class SPyShell(SPyIO):
    """
    Simple Python Shell (SPyS) implements an interactive, functional shell/REPL* extensible using a
    dynamically loading plugin architecture. [REPL = read-eval-print loop]
    
    Invocation of a new SPyS instance is accomplished by creating a new SPyS instance and calling 
    the start() method. On invocation, SPyS will start up an interactive command shell that provides
    a few utility functions:
        @load <module> - Dynamically load <module>, importing provided commands into the SPyS environment
        $! - If a command fails, $! will print the thrown exception, useful for debugging
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
        super(SPyShell, self).__init__(self)

        # THIS IS DEEP VOODOO
        # We're inspecting the stack to get the calling frame,
        # so we can interact with the calling instance's .shared property
        # (inherited from SPysIO). This seems like an inelegant and
        # brute-force way of doing things, if there's something better
        # either in implementation or architecturally to provide
        # a shared variable between instances I'd love to know it.
        # I'm trying to avoid doing things that would require BDSM
        # control of the plugin API, as I like the idea of being able
        # to freely bind damn near any function/class, without it having to
        # be special (i.e. I don't want to pass self in every @load etc).
        # While weird and abusive, this seems to be the most transparent and 
        # "magical" way of providing what is more or less shared memory.
        # The upshot of this whole thing is that the data in the .shared property
        # and the I/O endpoints transparently propagate into subshells invoked 
        # by the parent instance.
        callstack = inspect.stack()
        stacklen = len(callstack)
        try:
            myframe = callstack[stacklen - 2] # (len - 1) => this frame, (len - 2) => calling frame
            self.callinginstance = myframe[0].f_locals['self']
        except KeyError, IndexError:
            self.callinginstance = self # PIME TARADOX
        self.shared = self.callinginstance.shared
        self._outendpoints = self.callinginstance._outendpoints
        self._inendpoints = self.callinginstance._inendpoints

        self.__commands = {}
        self.__cmdhelp = {}
        self.__lastinput = FixedStack(20)
        self.__lastoutput = FixedStack(20)
        self.__trace = FixedStack(20)
        self.__exitcmds = ['exit', 'quit']

        self.binddefault()
        self.setprompt()

    def binddefault(self):
        """ Default command bindings """
        self.setcmd('$!', self.poptrace, 
                    "- Pops last exception off trace stack")
        self.setcmd('$i', self.popinput, 
                    "- Pops last input off of input stack")
        self.setcmd('$o', self.popoutput, 
                    "- Pops last object off of output stack")
        self.setcmd('/load', self.loadmodule, 
                    "<module> - Imports an extension")
        self.setcmd('/prompt', self.setprompt, 
                    "[string] - Sets interactive prompt to string, default if blank")
        self.setcmd('?', self.help, 
                    "- Displays help message")
        self.setcmd('/exec', self.execute, 
                    "<statement> - Execute a python statement")
        self.setcmd('/bind', self.bindfn, 
                    "<keyword> <string> - Bind inlined function in <string> to <keyword>")
        self.setcmd('/run', self.call, 
                    "<keyword> <keyword> <args> call <keyword> with output of <`keyword args`>")
        self.setcmd('/script', self.script, 
                    "<filename> - executes <filename> in shell")
        self.setcmd('.', lambda x:x, 
                    "<string> - Returns <string> literal")

    def help(self, arg):
        """ Command help implementation """ 
        if not arg:
            return "? <command> - Displays command help, if available\nAvailable commands: %s" % ", ".join(sorted(self.__commands.keys()))    
        if (arg in self.__commands) and (arg in self.__cmdhelp) and (self.__cmdhelp[arg]):
            return "%s %s" % (arg, self.__cmdhelp[arg])
        if arg not in self.__commands:
            return "%s is unbound" % arg
        
        return "No help for %s" % arg

    def script(self, input):
        try:
            file = open(input)
        except:
            return "Could not open input file"
        
        try:
            for line in file:
                self.handle(line.rstrip())
        except:
            return "Error reading input file"

    def setcmd(self, keyword, fn, help=None):
        if keyword and not fn:
            try:
                del(self.__commands[keyword])
                del(self.__cmdhelp[keyword])
            except IndexError:
                pass
        elif keyword and fn:
            self.__commands[keyword] = fn
            self.__cmdhelp[keyword] = help

    def setprompt(self, input=None):
        if input:
            self.__prompt = input
        else:
            self.__prompt = "spys> "

    def poptrace(self, input):
        item = self.__trace.pop()
        if item:
            return (str(item[0]), str(item[1]), str(item[2]))
        else:
            return "No exceptions on trace stack"

    def popinput(self, input):
        self.__lastinput.pop()        # pop first item because it's always going to be $i
        return self.__lastinput.pop()
    
    def popoutput(self, input):
        return self.__lastoutput.pop()
    
    def execute(self, input):
        try:
            exec input
        except Exception, e:
            self.__trace.append(('exec', input, e))
            return "Execution failed"

    def bindfn(self, input):
        (keyword, fn) = input.split(None, 1)
        expr = "self.setcmd('%s', %s, '''(bound function <<%s>>)''')" % (keyword, fn, fn)
        try:
            exec expr
            return "<<%s>> bound to '%s'" % (fn, keyword)
        except Exception, e:
            self.__trace.append(('bindfn', input, e))
            return "Bind failed"

    def call(self, input):
        (cmd, args) = input.split(None, 1)
        command = "%s %s" % (cmd, self.handle(args))
        self.output(command)
        return self.handle(command)

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

    def handle(self, input):
        if not input:
            return
        try:
            (cmd, args) = input.split(None, 1)
        except ValueError:
            cmd = input
            args = None

        if cmd in self.__commands.keys():
            try:
                if type(self.__commands[cmd]) == types.FunctionType and \
                "instance" in inspect.getargspec(self.__commands[cmd])[0]:
                    return self.__commands[cmd](args, self)
                else:
                    return self.__commands[cmd](args)
            except AttributeError or NameError, e:
                self.__trace.append((cmd, args, e))
                self.output(traceback.format_exc())
                return "Command '%s' failed" % cmd
            except ValueError or TypeError, e:
                self.__trace.append((cmd, args, e))
                self.output(traceback.format_exc())
                return "Bad argument '%s' for '%s'" % (args, cmd)
            except Exception, e:
                self.__trace.append((cmd, args, e))
                self.output(traceback.format_exc())
                return "Untrapped exception in '%s %s'" % (cmd, args)
        else:
            return self.default(input)
 
    def default(self, input):
        pass
 
    def oninput(self, input):
        pass

    def start(self, ret=None):
        while True:
            try:
                input = self.input(self.__prompt)
                self.oninput(input)
                self.__lastinput.append(input)
                if input in self.__exitcmds:
                    break

                result = self.handle(input)
                self.__lastoutput.append(result)
                if result:
                    self.output(result)
            except Exception, e:
                self.output(e)
        return ret
 
if __name__ == "__main__":
    s = SPyShell()
    s.start()
