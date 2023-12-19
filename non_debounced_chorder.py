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

CONFIG_INPUT_PINS = [
    mc.pin.GPIO1,
    mc.pin.GPIO5,
]

KEYS = []

CAN_CHORD = False
CHORD_TABLE = {
    (True, False): "a",
    (False, True): "b",
    (True, True): "c",
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
        print("No chord found")
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
    
    def update(self):
        if self.pin.value != self.lastvalue:
            # todo: debounce this
            
            self.onstatechange()
            self.lastvalue = self.pin.value
            
            return True
        
        return False
    
    def onstatechange(self):
        print("Change in state detected on pin", self.cpin, "to", "on" if self.pin.value else "off")
        
        if self.pin.value:
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
