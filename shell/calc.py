import shell

class Calc(shell.Shell):
    def __init__(self, arg=None):
        shell.Shell.__init__(self)
        self.stack = []
        self.setprompt("rpn> ")
        self.start()
    
    def dumpstack(self, limit=None):
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
        operands = "+-*/"
        buffer = []
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
                except e:
                    return "Bad mojo"
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

def ponies(arg):
    return "OMG PONIES!"

def exports():
    return [(__name__, "calc", Calc), 
            (__name__, "ponies", ponies)]

if __name__ == "__main__":
    calc = Calc()
    calc.start()
