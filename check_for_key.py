# Connect the switch to pin1 and ground

import board
import digitalio as dio
import microcontroller as mc
import time

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

kb = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kb)

pin = dio.DigitalInOut(mc.pin.GPIO1)
pin.direction = dio.Direction.INPUT
pin.pull = dio.Pull.UP

led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT

while True:
    led.value = pin.value
