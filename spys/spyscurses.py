import curses
scr = curses.initscr()
curses.start_color()
(scry, scrx) = scr.getmaxyx()
status = curses.newwin(1, scrx, 0, 0)
main = curses.newwin(scry - 2, scrx, 1, 0)
inp = curses.newwin(1, scrx, scry - 1, 0)
main.scrollok(True)
#curses.noecho()

scr.bkgdset(chr(49))
status.bkgdset(chr(50))

try:
    while True:
        main.addstr(inp.getstr() + "\n")
        inp.erase()
        main.bkgd(' ')
        status.bkgd('*')
        inp.bkgd(' ')
        main.refresh()
        status.refresh()
        inp.refresh()
except Exception, e:
    curses.nocbreak()
    scr.keypad(0)
    curses.echo()
    curses.endwin()
    print e
