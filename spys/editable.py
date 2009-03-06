import curses
 
class EditBuffer(object):
    """
    Provides display-independent sliding-window editable line buffer.
    """
    def __init__(self, string=None, prompt=None, viewport=None):
        self.cursor = 0
        self.killbuf = []
        
        try:
            self.vplen = int(viewport)
        except TypeError:
            self.vplen = 80
        
        if prompt:
            self.prompt = str(prompt)

        if string:
            self.buffer = list(str(string))
        else:
            self.buffer = []

    def __len__(self):
        return len(self.buffer)
 
    def __str__(self):
        return "".join(self.buffer)
 
    def dump(self):
        """ Debugging junk """
        print "cursor: %s, vpoffset: %s, vplen: %s" % (self.cursor, self.vpoff, self.vplen)
        print "contents: %s" % self.buffer
 
    def load(self, string):
        """ Load string into buffer and place cursor at end """
        if string:
            self.buffer = list(str(string))
            self.moveabs(len(self.buffer))
        else:
            self.buffer = []
            self.cursor = 0
        return self.render()

    def reset(self):
        """ Clear buffer and reset cursor to beginning """
        self.buffer = []
        self.cursor = 0
        return self.render()
    
    def yank(self):
        """ Insert contents of killbuf at cursor """
        try:
            self.buffer[self.cursor:self.cursor] = self.killbuf
            self.cursor = self.cursor + len(self.killbuf)
        except IndexError, e:
            pass
        return self.render()

    def kill(self):
        """ Cut buffer contents from cursor to end and save in killbuf """
        try:
            self.killbuf = self.buffer[self.cursor:]
            self.buffer = self.buffer[:self.cursor]
        except IndexError, e:
            pass
        return self.render()

    def backspace(self):
        """ Delete character behind cursor """
        try:
            if self.cursor > 0:
                self.moverel(-1)
                del(self.buffer[self.cursor])
            elif self.cursor == 0:
                pass
        except IndexError, e:
            pass
        return self.render()

    def delete(self):
        """ Delete character under cursor """
        try:
            del(self.buffer[self.cursor])
        except IndexError, e:
            pass
        return self.render()

    def moverel(self, dist):
        """ Move cursor relative to current position """
        newpos = self.cursor + dist
        if newpos < 0:
            newpos = 0
        self.moveabs(newpos)
        return self.cursor
    
    def moveabs(self, index):
        """ Move cursor to absolute index """
        if (index == -1) or (index > len(self.buffer)):
            self.cursor = len(self.buffer)
        elif index < 0:
            self.cursor = 0
        else:
            self.cursor = index
        
    def insert(self, char):
        """ 
        Insert character at current position pushing any character ahead of it
        forward, and growing the buffer as needed.
        """
        try:
            self.buffer.insert(self.cursor, char)
            self.moverel(1)
        except IndexError, e:
            pass
        return self.render()
    
    def vpcursor(self):
        """ Get cursor position relative to viewport """
        if self.cursor > (self.vplen - len(self.prompt)):
            return self.vplen
        elif self.cursor < 0:
            return 0 + len(self.prompt)
        else:
            return self.cursor + len(self.prompt)
            
    def render(self):
        """ Return string representation of sliding window viewport """
        start = self.cursor - self.vplen
        if start < 0:
            start = 0
        end = start + (self.vplen - len(self.prompt))
        if end > len(self.buffer):
            end = len(self.buffer)
        # replaces tabs with spaces cuz i'm lazy
        return self.prompt + "".join(self.buffer[start:end]).replace('\t', ' ')
 
class EditableWindow(object):
    """
    Provides line editing and command buffer functionality for curses windows
    with a subset of emacs key bindings. Untested with multi-line windows.
    """
    def __init__(self, window):
        self.window = window
        self.inbuf = []
        self.linebuf = []
        self.tempbuf = ""
        self.prompt = ""
        self.curline = 0
        (self.height, self.width) = self.window.getmaxyx()
        self.maxlen = self.width - 1
    
    def sync(self):
        """ [Hopefully] synchronize the screen with what's in the edit buffer """
        self.window.erase()
        self.window.addstr(self.inbuf.render())
        self.window.move(0, self.inbuf.vpcursor())
        self.window.refresh()
 
    def lastinput(self):
        """ Pull previous input from the buffer """
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

    def nextinput(self):
        """ Pull next input from the buffer """
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
 
    def input(self, prompt=None, echo=True):
        """ 
        Get stuff from terminal, returning stuff as string, with a
        minimal subset of emacs-style editing bindings.
        """
        self.inbuf = EditBuffer(prompt=prompt, viewport=self.maxlen)
        self.sync()
        while True:
            inc = self.window.getch()

            if inc in range(0x20, 0x7E): # printable ASCII
                self.inbuf.insert(chr(inc))
            elif inc in [curses.KEY_UP]: # up
                self.lastinput()
            elif inc in [curses.KEY_DOWN]: # down 
                self.nextinput()
            elif inc in [curses.KEY_LEFT]: # left
                self.inbuf.moverel(-1)
            elif inc in [curses.KEY_RIGHT]: # right
                self.inbuf.moverel(1)
            elif inc in [0x01]: # ctrl-a
                self.inbuf.moveabs(0)
            elif inc in [0x05]: # ctrl-e
                self.inbuf.moveabs(-1)
            elif inc in [0x0B]: # ctrl-k
                self.inbuf.kill()
            elif inc in [0x19]: # ctrl-y
                self.inbuf.yank()
            elif inc in [curses.KEY_BACKSPACE, 0x7F]: # backspace
                self.inbuf.backspace()
            elif inc in [curses.KEY_DC]: # delete
                self.inbuf.delete()
            elif inc in [0x0A]: # enter
                break
            else:
                curses.flash()
            
            # mask input by not syncing after input
            if echo:
                self.sync()
        # don't push masked input into command buffer
        if echo:
            if len(self.inbuf) > 0:
                self.linebuf.insert(0, str(self.inbuf))

        self.curline = 0
        self.tempbuf = ""
        return str(self.inbuf)
