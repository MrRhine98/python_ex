import curses

def main(stdscr):
       stdscr.clear()
       stdscr.addstr('OK!')
       char = stdscr.getch()

curses.wrapper(main)



