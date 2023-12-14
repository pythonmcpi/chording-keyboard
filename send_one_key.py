import board
import digitalio as dio
import time

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

kb = Keyboard(usb_hid.devices)

kb.send(Keycode.A)
