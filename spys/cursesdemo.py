import curses
import spys
"""
This sample demonstrates using SPyS I/O endpoints to build an interface
similar to `irssi` using the curses windowing library.
"""

screen = curses.initscr()
curses.start_color()
(wheight, wwidth) = screen.getmaxyx()

wstatus = curses.newwin(1, wwidth, 0, 0)
wmain = curses.newwin(wheight - 3, wwidth, 1, 0)
winfo = winp = curses.newwin(1, wwidth, wheight - 2, 0)
winp = curses.newwin(1, wwidth, wheight - 1, 0)

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
    wmain.addstr(str(string) + "\n")
    wrefresh()

def endp_winfo(string):
    """
    Output endpoint for info window.
    """
    winfo.erase()
    winfo.addstr(str(string), curses.color_pair(1))
    wrefresh()

def endp_winp(prompt):
    """
    Input endpoint for prompt window.
    """
    winp.erase()
    winp.addstr(prompt, curses.color_pair(2))
    wrefresh()
    return winp.getstr()

s = spys.SPyShell()
s.registerinput(0, endp_winp)
s.registeroutput(0, endp_wmain)
s.registeroutput(1, endp_wstatus)
s.registeroutput('info', endp_winfo)
s.output("main window (endpoint 0)", 0)
s.output("status window (endpoint 1)", 1)
s.output("info window (endpoint 'info')", 'info')
s.output("default endpoint")
s.start()
screen.keypad(0)
curses.nocbreak()
curses.echo()
curses.endwin()
