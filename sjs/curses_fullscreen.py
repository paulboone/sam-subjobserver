import curses

from contextlib import contextmanager

@contextmanager
def curses_fullscreen():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

    try:
        yield stdscr
    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
