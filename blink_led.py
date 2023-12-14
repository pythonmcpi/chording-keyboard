import board
import digitalio as dio
import time

pin = dio.DigitalInOut(board.LED)
pin.direction = dio.Direction.OUTPUT

LAST_TOGGLE = -1

while True:
    now = time.monotonic()
    if now >= LAST_TOGGLE + 0.5:
        pin.value = not pin.value
        LAST_TOGGLE = now
