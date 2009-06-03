import spys

class Calc(spys.SPyShell):
    """
    Implements a simple four function RPN calculator using SPyS.
    
    This demonstration implements a simple RPN calculator by
    inheriting from the SPyS interactive shell library.
    At the 'rpn>' prompt, enter a valid postfix-notation expression
    for evaluation.

    RPN commands (* indicates stack side effects):
          = -> Display the top element on the stack
          $ -> Display the entire stack
          x -> Clear the stack*
          ^ -> Pop the top element off the stack*
    +,-,*,/ -> Pop the top two elements off the top of the stack as (a, b)
               and perform (a opr b), pushing the result back on to the stack.*

    Example:
    rpn> 1 1 2 3 5 8 + - * / =
    0: -0.05
    """
    def __init__(self, arg=None):
        super(Calc, self).__init__(self)
        self.stack = []
        self.setprompt("rpn> ")
        self.start()
    
    def dumpstack(self, limit=None):
        """Pretty-print RPN stack, with indexes."""
        output = []
        if self.stack:
            index = 0
            for item in reversed(self.stack):
                output.append("%s: %s" % (index, item))
                index += 1
                if limit and (index >= limit):
                    break
            return "\n".join(output)
        else:
            return "Empty stack"

    def default(self, arg):
        """
        Main program loop, overrides SPyS default command handler
        method to implement interactive RPN calculator.
        """
        operands = "+-*/" # operator list, must be python operators
        buffer = [] # buffer for messages

        for word in arg.split(' '):
            if word == 'x':
                self.stack = []
                buffer.append(self.dumpstack())
            elif word == '^':
                return self.stack.pop()
            elif word in operands and (len(self.stack) >= 2):
                try:
                    b = str(self.stack.pop())
                    a = str(self.stack.pop())
                    self.stack.append(eval(a + word + b))
                    self.output(self.dumpstack(1) + " <-- top of stack", 1)
                except Exception, e:
                    self.error("Bad mojo", e)
            elif word == '$':
                buffer.append(self.dumpstack())
            elif word == '=':
                buffer.append(self.dumpstack(1))
            else:
                try:
                    self.stack.append(float(word))
                except ValueError:
                    return "Input must be an operator or a parseable number"
        return "\n\n".join(buffer)

def ponies():
    """
    Plain functions can be dynaloaded as well, with one caveat:
    input should only be done via the function argument, and
    output should only be done via return under most circumstances
    to keep things curses-safe.
    """
    return "OMG PONIES!"

def instancedemo(arg, instance=None):
    """
    Optional magic argument 'instance' can be passed, requesting the
    framework instance to pass itself so that the dynaloaded function
    has access to a 'self' analog.
    """
    return dir(instance)

def spys_exports():
    """
    spys_exports() describes module functionality to allow dynaloading by another SPyS REPL 
    instance using the @load command. Structure should be a list of tuples, each tuple
    containing the package name, the command name that will be exported to the loading
    SPyS environment, and finally the callable object itself. When @load <package> is
    called, the presence of this function will indicate this package is a SPyS plugin
    and will allow the parent to load and map the exported callables into itself.
    """
    return [(__name__, "calc", Calc), 
            (__name__, "ponies", ponies),
            (__name__, "instancedemo", instancedemo)]

if __name__ == "__main__":
    calc = Calc()
    calc.start()
