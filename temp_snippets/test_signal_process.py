# encoding: utf-8
import code
import traceback
import signal
import time

__author__ = 'yonka'


def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d = {'_frame': frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    # i = code.InteractiveConsole(d)
    message = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    # i.interact(message)
    print message


def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler


def main():
    listen()
    while True:
        time.sleep(2)
        print 123


if __name__ == "__main__":
    main()
