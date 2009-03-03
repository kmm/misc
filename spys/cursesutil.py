import curses

class WindowCompleter(object):
    """
    Provides some readline like functionality for curses windows.
    """
    def __init__(self, window):
        self.dispatch = {}
        self.window = window
        self.linebuf = []
        self.curline = 0
        self.inbuf = ""
        self.tempbuf = ""
        self.cpos = 0 # cursor position (x)
        self.cbuf = 0 # buffer position (offset)
        (self.height, self.width) = self.window.getmaxyx()
        self.maxlen = self.width - 1
        self.prompt = ""
        self.terminator = 0x0A
    
    def renderlong(self, string, offset=0):
        if (len(self.prompt) + len(string)) > self.maxlen:
            self.window.erase()
            #self.window.addstr(self.prompt)
            self.window.addstr(string[offset:(self.maxlen - len(self.prompt))+offset])
        else:
            self.window.erase()
            #self.window.addstr(self.prompt)
            self.window.addstr(string)

    def lastinput(self):
        try:
            self.inbuf = self.linebuf[self.curline]
            if self.curline < len(self.linebuf) - 1:
                self.curline += 1
        except IndexError:
            try:
                self.inbuf = self.linebuf[-1]
            except IndexError:
                self.curline = 0
                self.inbuf = self.tempbuf
        print "%s/%s" % (self.curline, len(self.linebuf))
        self.renderlong(self.inbuf)

    def nextinput(self):
        if self.curline == 0:
            curses.flash()
            self.inbuf = self.tempbuf
        elif self.curline > 0:
            try:
                self.inbuf = self.linebuf[self.curline - 1]
                self.curline -= 1
            except IndexError:
                self.inbuf = self.tempbuf
        else:
            curses.flash()
        
        self.renderlong(self.inbuf)

    def enter(self):
        self.window.erase()

    def backspace(self):
        self.inbuf = self.inbuf[:len(self.inbuf) - 1]
        self.renderlong(self.inbuf)

    def default(self, charcode):
        self.inbuf += chr(charcode)
        self.tempbuf = self.inbuf
        self.renderlong(self.inbuf)

    def input(self, prompt=None):
        if prompt:
            self.prompt = prompt
        self.inbuf = ""
        self.renderlong(self.inbuf)

        while True:
            inc = self.window.getch()
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
                (y, x) = self.window.getyx()
                self.window.move(y, x - 1)
            elif inc == curses.KEY_RIGHT:
                (y, x) = self.window.getyx()
                self.window.move(y, x + 1)
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
            self.linebuf.insert(0, self.inbuf)
        return self.inbuf
