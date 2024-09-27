import time
from pynput import keyboard, mouse

# Global Variables
DEBUG_MODE = False  # Set to True to enable step/input messages

# Variables to track the state
a_pressed = False
d_pressed = False
waiting_for_opposite = False
waiting_for_shot = False

# Time variables
first_key = None          # Holds 'A' or 'D' for the first key pressed
opposite_key_press_time = None
mouse_press_time = None
mouse_release_time = None

# List to store results
results = []

# Print table header
print(f"{'Direction':>10} | {'Shot Delay (ms)':>15} | {'Spray Time (ms)':>15}")
print("-" * 45)

def on_key_press(key):
    global a_pressed, d_pressed, waiting_for_opposite, opposite_key_press_time, waiting_for_shot, first_key

    try:
        if key.char == 'a':
            if first_key is None:
                # First key press
                a_pressed = True
                first_key = 'A'
                if DEBUG_MODE:
                    print("Step 1: 'A' pressed")
            elif first_key == 'D' and waiting_for_opposite:
                # Pressed 'A' after releasing 'D'
                opposite_key_press_time = time.time()
                if DEBUG_MODE:
                    print("Step 2: 'A' pressed after releasing 'D'")
                waiting_for_shot = True
            a_pressed = True  # Update a_pressed
        elif key.char == 'd':
            if first_key is None:
                # First key press
                d_pressed = True
                first_key = 'D'
                if DEBUG_MODE:
                    print("Step 1: 'D' pressed")
            elif first_key == 'A' and waiting_for_opposite:
                # Pressed 'D' after releasing 'A'
                opposite_key_press_time = time.time()
                if DEBUG_MODE:
                    print("Step 2: 'D' pressed after releasing 'A'")
                waiting_for_shot = True
            d_pressed = True  # Update d_pressed
    except AttributeError:
        pass  # Ignore special keys

def on_key_release(key):
    global a_pressed, d_pressed, waiting_for_opposite

    try:
        if key.char == 'a':
            if a_pressed:
                a_pressed = False
                waiting_for_opposite = True
                if DEBUG_MODE:
                    print("Step 2: 'A' released, waiting for 'D'")
        elif key.char == 'd':
            if d_pressed:
                d_pressed = False
                waiting_for_opposite = True
                if DEBUG_MODE:
                    print("Step 2: 'D' released, waiting for 'A'")
    except AttributeError:
        pass  # Ignore special keys

def on_click(x, y, button, pressed):
    global mouse_press_time, mouse_release_time, waiting_for_shot

    if button == mouse.Button.left and waiting_for_shot:
        try:
            if pressed:
                mouse_press_time = time.time()
                if DEBUG_MODE:
                    print("Mouse button pressed")
            else:
                mouse_release_time = time.time()
                if mouse_press_time and opposite_key_press_time:
                    shot_delay = (mouse_press_time - opposite_key_press_time) * 1000  # Convert to ms
                    spray_time = (mouse_release_time - mouse_press_time) * 1000  # Convert to ms

                    # Determine peek direction
                    if first_key == 'A':
                        direction = 'Left'  # A→D
                    elif first_key == 'D':
                        direction = 'Right'  # D→A
                    else:
                        direction = 'Unknown'

                    # Store the results
                    results.append((direction, shot_delay, spray_time))

                    # Print the results in a formatted table row
                    print(f"{direction:>10} | {shot_delay:15.2f} | {spray_time:15.2f}")

                else:
                    if DEBUG_MODE:
                        print("Timing data incomplete. Please try again.")
                reset_variables()
        except Exception as e:
            if DEBUG_MODE:
                print(f"An error occurred in on_click: {e}")
            reset_variables()

def reset_variables():
    global a_pressed, d_pressed, waiting_for_opposite, waiting_for_shot
    global first_key, opposite_key_press_time, mouse_press_time, mouse_release_time

    a_pressed = False
    d_pressed = False
    waiting_for_opposite = False
    waiting_for_shot = False

    first_key = None
    opposite_key_press_time = None
    mouse_press_time = None
    mouse_release_time = None

def main():
    print("Program started. Press 'Ctrl+C' to exit.")
    # Start the listeners without blocking the main thread
    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

    try:
        while True:
            time.sleep(0.1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        keyboard_listener.stop()
        mouse_listener.stop()

if __name__ == "__main__":
    main()
