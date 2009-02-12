import shell

class Calc(shell.Shell):
    def __init__(self, arg):
        shell.Shell.__init__(self)
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
