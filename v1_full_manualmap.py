# See v1_full_manualmap.csv for a table of chords that can be imported into a spreadsheet program

import board
import digitalio as dio
import microcontroller as mc
import time
import supervisor

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
#from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

kb = Keyboard(usb_hid.devices)
#layout = KeyboardLayoutUS(kb)

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
    (False, False, False, True, False, False, False): Keycode.E,
    (False, False, True, False, False, False, False): Keycode.I,
    (False, True, False, False, False, False, False): Keycode.A,
    (True, False, False, False, False, False, False): Keycode.S,
    (False, False, True, True, False, False, False): Keycode.R,
    (False, True, True, False, False, False, False): Keycode.N,
    (True, True, False, False, False, False, False): Keycode.T,
    (False, True, False, True, False, False, False): Keycode.O,
    (True, False, True, False, False, False, False): Keycode.L,
    (True, False, False, True, False, False, False): Keycode.C,
    (False, True, True, True, False, False, False): Keycode.D,
    (True, True, True, False, False, False, False): Keycode.P,
    (True, True, True, True, False, False, False): Keycode.U,
    (False, False, False, True, False, True, False): Keycode.M,
    (False, False, True, False, False, True, False): Keycode.G,
    (False, True, False, False, False, True, False): Keycode.H,
    (True, False, False, False, False, True, False): Keycode.B,
    (False, False, True, True, False, True, False): Keycode.Y,
    (False, True, True, False, False, True, False): Keycode.F,
    (True, True, False, False, False, True, False): Keycode.V,
    (False, True, False, True, False, True, False): Keycode.W,
    (True, False, True, False, False, True, False): Keycode.K,
    (True, False, False, True, False, True, False): Keycode.X,
    (False, True, True, True, False, True, False): Keycode.J,
    (True, True, True, False, False, True, False): Keycode.Z,
    (True, True, True, True, False, True, False): Keycode.Q,
    (False, False, False, True, True, False, False): Keycode.SPACE,
    (False, False, True, False, True, False, False): Keycode.TAB,
    (False, False, False, False, False, True, False): Keycode.SHIFT,
    (False, False, False, False, True, False, False): Keycode.ALT,
    (False, False, False, False, False, False, True): Keycode.CONTROL,
    (False, False, True, True, True, False, False): Keycode.ENTER,
    (False, False, False, True, False, False, True): Keycode.ONE,
    (False, False, True, False, False, False, True): Keycode.TWO,
    (False, True, False, False, False, False, True): Keycode.THREE,
    (True, False, False, False, False, False, True): Keycode.FOUR,
    (False, False, True, True, False, False, True): Keycode.FIVE,
    (False, True, True, False, False, False, True): Keycode.SIX,
    (True, True, False, False, False, False, True): Keycode.SEVEN,
    (False, True, False, True, False, False, True): Keycode.EIGHT,
    (True, False, True, False, False, False, True): Keycode.NINE,
    (False, True, True, True, False, False, True): Keycode.ZERO,
    (False, True, False, False, True, False, False): Keycode.PERIOD,
    (False, True, False, True, True, False, False): Keycode.COMMA,
    (True, True, False, False, True, False, False): Keycode.FORWARD_SLASH,
    (True, True, True, True, True, False, False): Keycode.GRAVE_ACCENT,
    (True, False, False, False, True, False, False): Keycode.MINUS,
    (False, True, True, True, True, False, False): Keycode.EQUALS,
    (True, False, True, False, True, False, False): Keycode.LEFT_BRACKET,
    (True, False, False, True, True, False, False): Keycode.RIGHT_BRACKET,
    (True, True, True, False, True, False, False): Keycode.BACKSLASH,
    (True, True, False, True, True, False, False): Keycode.SEMICOLON,
    (True, False, True, True, True, False, False): Keycode.QUOTE,
    (False, True, True, False, True, False, False): Keycode.BACKSPACE,
    (True, False, True, True, False, False, True): Keycode.RIGHT_ARROW,
    (True, True, False, True, False, False, True): Keycode.LEFT_ARROW,
    (True, False, False, True, False, False, True): Keycode.UP_ARROW,
    (True, True, True, True, False, False, True): Keycode.DOWN_ARROW,
    (True, True, True, False, False, False, True): Keycode.ESCAPE,
    (True, False, True, True, False, False, False): Keycode.HOME,
    (True, True, False, True, False, False, False): Keycode.END,
    (True, True, False, True, False, True, False): Keycode.WINDOWS,
    (True, False, True, True, False, True, False): Keycode.DELETE,
}

current_modifiers = 0
sticky_modifiers = 0
last_modifier = 0
start_time = time.monotonic_ns() # Reference point
last_modifier_time = time.monotonic_ns()

def send_kb_report():
    kb.report_modifier[0] = current_modifiers
    kb._keyboard_device.send_report(kb.report)

def prime_chord():
    global CAN_CHORD

    CAN_CHORD = True

def send_chord():
    global CAN_CHORD
    global last_modifier
    global last_modifier_time
    global current_modifiers
    global sticky_modifiers

    if not CAN_CHORD:
        # We need this, otherwise keyups for one chord would trigger multiple chords
        return

    # CHORD_TABLE uses True if the key was pressed, while the actual pins
    # say True if the key is not pressed. So we invert it.
    current_key_comb = tuple(not key.lastvalue for key in KEYS)

    try:
        # We can index dicts with immutable values such as tuples
        key_to_send = CHORD_TABLE[current_key_comb]
    except KeyError:
        # No chord found
        # Don't reset CAN_CHORD
        print("No chord found:", current_key_comb)
        return

    CAN_CHORD = False

    print("Sending text:", key_to_send)

    #layout.write(key_to_send)
    modifier = Keycode.modifier_bit(key_to_send)
    if modifier:
        if modifier & sticky_modifiers:
            # Was sticky, turn it off
            sticky_modifiers &= ~modifier
            current_modifiers &= ~modifier
            
            # Tell the os about the modifier key update (stuff for shift+mouse scroll)
            send_kb_report()
            
            print("Unsticked modifier", modifier)
            return
        
        # If double tap - two taps of the same key within 500ms
        if modifier == last_modifier and time.monotonic_ns() - last_modifier_time < 5e8:
            sticky_modifiers |= modifier
            current_modifiers |= modifier
            
            send_kb_report()
            
            print("Stickied modifier", modifier)
        else:
            # Toggle the modifier bit (in internal state - reference https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/main/adafruit_hid/keyboard.py)
            current_modifiers ^= modifier
            send_kb_report()
            
            print("Toggled modifier", modifier, "to", current_modifiers & modifier)
            
            # Tracking for double tap detection
            last_modifier = modifier
            last_modifier_time = time.monotonic_ns()
    else:
        kb.report_modifier[0] = current_modifiers
        kb.press(key_to_send)
        kb.release(key_to_send)
        current_modifiers = sticky_modifiers # Remove non-sticky modifier keys
        
        # Tell the os about the released modifier keys
        send_kb_report()
        
        # And since this wasn't a modifier, reset the double tap timer
        last_modifier_time = start_time

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
