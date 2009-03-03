
import curses
import editable
import spys
import sys
"""
This sample demonstrates using SPyS I/O endpoints to build an interface
similar to `irssi` using the curses windowing library.
"""
screen = curses.initscr()

curses.start_color()
curses.noecho()
(wheight, wwidth) = screen.getmaxyx()

wstatus = curses.newwin(1, wwidth, 0, 0)
wmain = curses.newwin(wheight - 3, wwidth, 1, 0)
winfo = winp = curses.newwin(1, wwidth, wheight - 2, 0)
winp = curses.newwin(1, wwidth, wheight - 1, 0)
winp.keypad(True)

curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
curses.init_pair(2, curses.COLOR_CYAN, 0)

wmain.scrollok(True)

wstatus.bkgd(' ', curses.color_pair(1))
wmain.bkgd(' ')
winfo.bkgd(' ', curses.color_pair(1))
winp.bkgd(' ')

def wrefresh():
    wstatus.refresh()
    wmain.refresh()
    winfo.refresh()
    winp.refresh()

def endp_wstatus(string):
    """
    Output endpoint for status window.
    """
    wstatus.erase()
    wstatus.addstr(str(string), curses.color_pair(1))
    wrefresh()
    
def endp_wmain(string):
    """
    Output endpoint for main window.
    """
    if str(string).endswith("\n"):
        wmain.addstr(str(string))
    else:
        wmain.addstr(str(string) + "\n")
    wrefresh()

def endp_winfo(string):
    """
    Output endpoint for info window.
    """
    winfo.erase()
    winfo.addstr(str(string), curses.color_pair(1))
    wrefresh()

def clear(junk):
    wmain.erase()

s = spys.SPyShell()
c = editable.WindowCompleter(winp)

# steal stdX so print/read get redirected to curses
class ProxyStdIO(object):
    def write(self, string):
        s.output(string)

    def readline(self):
        return c.input()
proxy = ProxyStdIO()
sys.stdin = proxy
sys.stdout = proxy
sys.stderr = proxy

s.registerinput(0, c.input)
s.registeroutput(0, endp_wmain)
s.registeroutput(1, endp_wstatus)
s.registeroutput('info', endp_winfo)
s.output("main window (endpoint 0)", 0)
s.output("status window (endpoint 1)", 1)
s.output("info window (endpoint 'info')", 'info')
s.output("default endpoint")
s.setcmd("clear", clear)
print "this should get proxied to default"
s.start()

# restore stdX so curses can unfuck the terminal
sys.stdout = sys.__stdout__
sys.stdin = sys.__stdin__
sys.stderr = sys.__stderr__

screen.keypad(False)
curses.nocbreak()
curses.echo()
curses.endwin()
