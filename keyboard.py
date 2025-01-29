from collections.abc import Callable

from pynput import keyboard
import threading


def start_listener(on_press: Callable[[keyboard.Key], None], on_release: Callable[[keyboard.Key], None]):
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    # ...or, in a non-blocking fashion:
    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()


def listen(on_press: Callable[[keyboard.Key], None], on_release: Callable[[keyboard.Key], None]) -> None:
    thread = threading.Thread(target=start_listener, args=(on_press, on_release))
    thread.start()
