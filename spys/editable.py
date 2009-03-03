import curses

class EditBuffer(object):
    def __init__(self, string=None):
        self.cursor = 0
        self.vplen = 30 # viewport length
        self.vpoff = 0  # viewport offset
        if string:
            self.buffer = list(str(string))
        else:
            self.buffer = []

    def __len__(self):
        return len(self.buffer)

    def __str__(self):
        return "".join(self.buffer)

    def dump(self):
        print "cursor: %s, vpoffset: %s, vplen: %s" % (self.cursor, self.vpoff, self.vplen)
        print "contents: %s" % self.buffer

    def load(self, string):
        if string:
            self.buffer = list(str(string))
            self.cursor = len(self.buffer) - 1
        else:
            self.buffer = []
            self.cursor = 0
    
    def reset(self):
        self.buffer = []
        self.cursor = 0
    
    def backspace(self):
        if self.cursor > 0:
            self.cursor -= 1
            try:
                del(self.buffer[self.cursor])
            except IndexError:
                pass

    def moverel(self, dist):
        newpos = self.cursor + dist
        if newpos < 0:
            self.cursor = 0
            self.vpoff = 0
        elif newpos > len(self.buffer) - 1:
            self.cursor = len(self.buffer) - 1
        else:
            self.cursor = newpos
        return self.cursor

    def moveabs(self, index):
        if index < 0:
            self.cursor = 0
        elif index > len(self.buffer) - 1:
            self.cursor = len(self.buffer) - 1
        else:
            self.cursor = index

    def insert(self, char):
        try:
            self.moverel(1)
            self.buffer.insert(self.cursor, char)
        except IndexError:
            pass

    def render(self):
        start = self.vpoff
        end = self.vpoff + self.vplen
        if end > len(self.buffer) - 1:
            end = len(self.buffer) - 1
        return "".join(self.buffer[start:end])

class WindowCompleter(object):
    """
    Provides some readline like functionality for curses windows.
    """
    def __init__(self, window):
        self.dispatch = {}
        self.window = window
        self.linebuf = []
        self.curline = 0
        self.inbuf = []
        self.tempbuf = ""
        self.cpos = 0 # cursor position (x)
        self.cbuf = 0 # buffer position (offset)
        (self.height, self.width) = self.window.getmaxyx()
        self.maxlen = self.width - 1
        self.prompt = ""
        self.terminator = 0x0A

    def render(self, string):
        self.window.erase()
        self.window.addstr(string)

    def lastinput(self):
        try:
            self.inbuf.load(self.linebuf[self.curline])
            if self.curline < len(self.linebuf) - 1:
                self.curline += 1
        except IndexError:
            try:
                self.inbuf.load(self.linebuf[-1])
            except IndexError:
                self.curline = 0
                self.inbuf.load(self.tempbuf)
        print "%s/%s" % (self.curline, len(self.linebuf))
        self.renderlong(self.inbuf.render())

    def nextinput(self):
        if self.curline == 0:
            curses.flash()
            self.inbuf.load(self.tempbuf)
        elif self.curline > 0:
            try:
                self.inbuf.load(self.linebuf[self.curline - 1])
                self.curline -= 1
            except IndexError:
                self.inbuf.load(self.tempbuf)
        else:
            curses.flash()
        self.renderlong(self.inbuf.render())

    def enter(self):
        pass

    def backspace(self):
        self.inbuf.backspace()
        print self.inbuf.dump()

    def default(self, charcode):
        self.inbuf.insert(chr(charcode))
        print self.inbuf.dump()

    def input(self, prompt=None):
        if prompt:
            self.prompt = prompt
        self.inbuf = EditBuffer()
        self.render(self.inbuf.render())

        while True:
            inc = self.window.getch()
            (y, x) = self.window.getyx()
            self.cpos = x
            if inc == curses.KEY_HOME:
                index = 0
                for element in self.linebuf:
                    print "%s: %s" % (index, element),
                    index += 1
                print "curline: %s/%s, inbuf: %s" % (self.curline, len(self.linebuf), self.inbuf),
            elif inc == curses.KEY_UP:
                self.lastinput()
            elif inc == curses.KEY_DOWN:
                self.nextinput()
            elif inc == curses.KEY_LEFT:
                self.window.move(y, x - 1)
                self.inbuf.moverel(-1)
            elif inc == curses.KEY_RIGHT:
                self.window.move(y, x + 1)
                self.inbuf.moverel(-1)
            elif inc == self.terminator:
                self.enter()
                break
            elif inc == curses.KEY_BACKSPACE:
                self.backspace()
            elif inc >= 0 and inc <= 255:
                self.default(inc)
            else:
                pass
                
        self.curline = 0
        self.tempbuf = ""
        if len(self.inbuf) > 0:
            self.linebuf.insert(0, str(self.inbuf))
        print str(self.inbuf)
        return str(self.inbuf)
