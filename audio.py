from collections.abc import Callable
from typing import Any

import numpy as np
import sounddevice as sd


data = None


def query_devices():
    return sd.query_devices()


def register_input_callback(device: int, callback: Callable[[np.ndarray, Any, Any, Any], None]):
    with sd.InputStream(device=device, channels=1, callback=callback, blocksize=512):
        print('-' * 80)
        print('press Return to quit')
        print('-' * 80)
        input()


def register_output_callback(device: int, callback: Callable[[np.ndarray, Any, Any, Any], None]):
    with sd.OutputStream(device=device, channels=16, callback=callback, blocksize=512):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()

def in_callback(indata, *args):
    global data
    data = indata


def out_callback(outdata, *args):
    if data is not None:
        outdata[:] = data


if __name__ == "__main__":
    with sd.InputStream(device=1, channels=1, callback=in_callback):
        with sd.OutputStream(device=2, channels=2, callback=out_callback):
            print('#' * 80)
            print('press Return to quit')
            print('#' * 80)
            input()
