import board
import digitalio as dio
import microcontroller as mc
import time
import supervisor

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

kb = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kb)

DEBOUNCE_DURATION = 30_000_000

CONFIG_INPUT_PINS = [
    mc.pin.GPIO0, # Pinky finger
    mc.pin.GPIO1, # Ring finger
    mc.pin.GPIO2, # Middle finger
    mc.pin.GPIO3, # Index finger
    mc.pin.GPIO4, # Leftmost thumb
    mc.pin.GPIO5, # Middle thumb
    mc.pin.GPIO6, # Rightmost thumb
]

KEYS = []

CAN_CHORD = False
CHORD_TABLE = {
    #(True, True, False, False, False, False, False): "h",
    #(True, False, False, False, False, False, False): "a",
    #(False, True, False, False, False, False, False): "b",
    #(False, False, True, False, False, False, False): "c",
    #(False, False, False, True, False, False, False): "d",
    #(False, False, False, False, True, False, False): "e",
    #(False, False, False, False, False, True, False): "f",
    #(False, False, False, False, False, False, True): "g",
    (False, False, False, True, False, False, False): "e",
    (False, False, True, False, False, False, False): "i",
    (False, True, False, False, False, False, False): "a",
    (True, False, False, False, False, False, False): "s",
    (False, False, True, True, False, False, False): "r",
    (False, True, True, False, False, False, False): "n",
    (True, True, False, False, False, False, False): "t",
    (False, True, False, True, False, False, False): "o",
    (True, False, True, False, False, False, False): "l",
    (True, False, False, True, False, False, False): "c",
    (False, True, True, True, False, False, False): "d",
    (True, True, True, False, False, False, False): "p",
    (True, True, True, True, False, False, False): "u",
    (False, False, False, True, False, True, False): "m",
    (False, False, True, False, False, True, False): "g",
    (False, True, False, False, False, True, False): "h",
    (True, False, False, False, False, True, False): "b",
    (False, False, True, True, False, True, False): "y",
    (False, True, True, False, False, True, False): "f",
    (True, True, False, False, False, True, False): "v",
    (False, True, False, True, False, True, False): "w",
    (True, False, True, False, False, True, False): "k",
    (True, False, False, True, False, True, False): "x",
    (False, True, True, True, False, True, False): "j",
    (True, True, True, False, False, True, False): "z",
    (True, True, True, True, False, True, False): "q",
    (False, False, False, True, True, False, False): " ",
    (False, False, True, False, True, False, False): "\t",
    (False, False, False, False, False, True, False): "Shift", # todo: toggles
    (False, False, False, False, True, False, False): "Alt",
    (False, False, False, False, False, False, True): "Control",
    (False, False, False, False, False, False, False): "Capslock",
    (False, False, True, True, True, False, False): "\n",
    (False, False, False, True, False, False, True): "1",
    (False, False, True, False, False, False, True): "2",
    (False, True, False, False, False, False, True): "3",
    (True, False, False, False, False, False, True): "4",
    (False, False, True, True, False, False, True): "5",
    (False, True, True, False, False, False, True): "6",
    (True, True, False, False, False, False, True): "7",
    (False, True, False, True, False, False, True): "8",
    (True, False, True, False, False, False, True): "9",
    (False, True, True, True, False, False, True): "0",
    (False, True, False, False, True, False, False): ".",
    (False, True, False, True, True, False, False): ",",
    (True, False, True, False, True, False, False): "?",
    (False, True, True, False, True, False, False): "!",
    (True, False, False, False, True, False, False): "~",
    (False, True, True, True, True, False, False): "`",
    (True, True, False, False, True, False, False): "@",
    (True, True, True, False, True, False, False): "#",
    (False, False, False, False, False, False, False): "$",
    (False, False, False, False, False, False, False): "%",
    (False, False, False, False, False, False, False): "^",
    (False, False, False, False, False, False, False): "&",
    (False, False, False, False, False, False, False): "*",
    (False, False, False, False, False, False, False): "(",
    (False, False, False, False, False, False, False): ")",
    (False, False, False, False, False, False, False): "-",
    (False, False, False, False, False, False, False): "_",
    (False, False, False, False, False, False, False): "=",
    (False, False, False, False, False, False, False): "+",
    (False, False, False, False, False, False, False): "[",
    (False, False, False, False, False, False, False): "]",
    (False, False, False, False, False, False, False): "{",
    (False, False, False, False, False, False, False): "}",
    (False, False, False, False, False, False, False): "\\",
    (False, False, False, False, False, False, False): "|",
    (False, False, False, False, False, False, False): "<",
    (False, False, False, False, False, False, False): ">",
    (False, False, False, False, False, False, False): "/",
    (False, False, False, False, False, False, False): ":",
    (False, False, False, False, False, False, False): ";",
    (False, False, False, False, False, False, False): "'",
    (False, False, False, False, False, False, False): '"',
    (False, False, False, False, False, False, False): "Delete",
    (False, False, False, False, False, False, False): "Home",
    (False, False, False, False, False, False, False): "End",
    (False, False, False, False, False, False, False): "PageUp",
    (False, False, False, False, False, False, False): "PageDown",
    (False, False, False, False, False, False, False): "Insert",
    (False, False, False, False, False, False, False): "Esc",
    (False, False, False, False, False, False, False): "Meta/Windows",
    (False, False, False, False, False, False, False): "F1",
    (False, False, False, False, False, False, False): "F2",
    (False, False, False, False, False, False, False): "F3",
    (False, False, False, False, False, False, False): "F4",
    (False, False, False, False, False, False, False): "F5",
    (False, False, False, False, False, False, False): "F6",
    (False, False, False, False, False, False, False): "F7",
    (False, False, False, False, False, False, False): "F8",
    (False, False, False, False, False, False, False): "F9",
    (False, False, False, False, False, False, False): "F10",
    (False, False, False, False, False, False, False): "F11",
    (False, False, False, False, False, False, False): "F12",
}

def prime_chord():
    global CAN_CHORD

    CAN_CHORD = True

def send_chord():
    global CAN_CHORD

    if not CAN_CHORD:
        # We need this, otherwise keyups for one chord would trigger multiple chords
        return

    # CHORD_TABLE uses True if the key was pressed, while the actual pins
    # say True if the key is not pressed. So we invert it.
    current_key_comb = tuple(not key.lastvalue for key in KEYS)

    try:
        # We can index dicts with immutable values such as tuples
        text_to_send = CHORD_TABLE[current_key_comb]
    except KeyError:
        # No chord found
        # Don't reset CAN_CHORD
        print("No chord found:", current_key_comb)
        return

    CAN_CHORD = False

    print("Sending text:", text_to_send)

    layout.write(text_to_send)

class Key:
    def __init__(self, cpin):
        self.cpin = cpin

        pin = dio.DigitalInOut(cpin)
        pin.direction = dio.Direction.INPUT
        pin.pull = dio.Pull.UP

        self.pin = pin
        self.lastvalue = pin.value
        self.value = self.lastvalue
        self.lastchange = time.monotonic_ns()

    def update(self):
        self.value = self.pin.value
        if self.value != self.lastvalue:
            tnow = time.monotonic_ns()
            if tnow < self.lastchange + DEBOUNCE_DURATION:
                return False

            self.lastchange = tnow

            self.onstatechange()
            self.lastvalue = self.value

            return True

        return False

    def onstatechange(self):
        print("Change in state detected on pin", self.cpin, "to", "on" if self.value else "off", "(last value was", "on" if self.lastvalue else "off", ")")

        if self.value:
            # Keyup (nonpressed = high)
            # Look for a chord match and send it
            send_chord()
        else:
            # Keydown
            # Allow a chord to be sent
            prime_chord()

for cpin in CONFIG_INPUT_PINS:
    KEYS.append(Key(cpin))

led = dio.DigitalInOut(board.LED)
led.direction = dio.Direction.OUTPUT

finished = False

while not finished:
    led.value = KEYS[0].pin.value
    for key in KEYS:
        key.update()
