import readline
import pdb
 
class Shell:
    __commands = None
    trace = None
 
    prompt = None
    exitcmd = None
 
    def __init__(self):
        self.__commands = {}
        self.__commands['!'] = self.poptrace

        self.trace = []
        
        self.prompt = "> "
        self.exitcmd = "exit"

    def setcmd(self, keyword, fn):
        if keyword and not fn:
            del(__commands[keyword])
        if keyword and fn:
            self.__commands[keyword] = fn


    def poptrace(self, input):
        if len(self.trace) == 0:
            return "No exceptions on stack."
        else:
            return self.trace.pop()
 
    def completer(self, input, state):
        options = [c for c in self.__commands.keys() if c.startswith(input)]
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

        if cmd in self.__commands.keys():
            try:
                return self.__commands[cmd](args)
            except AttributeError or NameError, e:
                # lists have pop() but no push()! wtf?
                self.trace.append(e)
                return "Command '%s' failed" % cmd
            except TypeError, e:
                self.trace.append(e)
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
                input = raw_input(self.prompt)
                
                if input == self.exitcmd:
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
    
    class Calc(Shell):
        def __init__(self, arg):
            Shell.__init__(self)
            self.stack = []
            self.prompt = "calc> "
            self.setcmd('>', self.stackpop)
            self.start()

        def default(self, arg):
            operands = "+-*/"
            if arg.empty:
                return self.stack

            for word in arg.split(' '):
                if word in operands and (len(self.stack) >= 2):
                    try:
                        b = str(self.stack.pop())
                        a = str(self.stack.pop())
                        print a + word + b
                        self.stack.append(eval(a + word + b))
                    except e:
                        return "Bad mojo"
                else:
                    try:
                        self.stack.append(float(word))
                    except ValueError:
                        return "Input must be an operator or a parseable number"
            
            return self.stack

        def stackpop(self, arg):
            try:
                return self.stack.pop()
            except IndexError:
                return None

    def subshell(arg):
        ss = Shell()
        ss.prompt = "subshell> "
        ss.setcmd('hex', lambda x: "0x%x" % int(x))
        ss.start("Subshell")

    s.setcmd('sqr', lambda x: int(x) * int(x))
    s.setcmd('subshell', subshell)
    s.setcmd('calc', Calc)
    s.start()

