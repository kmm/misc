import readline


class Shell:
    commands = [("demo", self['demo'])]
    prompt = "> "

    def __init__(self):
        pass

    def completer(self, input, state):
        options = [cmd[0] for cmd in self.commands if cmd[0].startswith(input)]
        try:
            return options[state]
        except IndexError:
            return None

    def start(self):
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")

        while True:
            input = raw_input(self.prompt)
            print input
