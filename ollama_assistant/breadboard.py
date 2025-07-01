import gpiod
import time

LED_PIN = 17
BUTTON_PIN = 27

# Try to find the correct Direction enum
def get_direction_enum():
    """Find the correct Direction enum values"""
    # Try different possible locations for Direction enum
    possible_locations = [
        ('gpiod.line.Direction', lambda: gpiod.line.Direction),
        ('gpiod.Direction', lambda: gpiod.Direction),
        ('gpiod.line_settings.Direction', lambda: gpiod.line_settings.Direction),
    ]
    
    for name, getter in possible_locations:
        try:
            direction_enum = getter()
            return direction_enum
        except AttributeError:
            continue
    
    # If no enum found, return None
    return None

# Try to find the correct Value enum
def get_value_enum():
    """Find the correct Value enum values"""
    possible_locations = [
        ('gpiod.line.Value', lambda: gpiod.line.Value),
        ('gpiod.Value', lambda: gpiod.Value),
        ('gpiod.line_settings.Value', lambda: gpiod.line_settings.Value),
    ]
    
    for name, getter in possible_locations:
        try:
            value_enum = getter()
            return value_enum
        except AttributeError:
            continue
    
    return None

# Get the enums
DIRECTION = get_direction_enum()
VALUE = get_value_enum()

def debug_enums():
    """Debug function to show what enums are available"""
    print("=== Debug Info ===")
    print("Available gpiod attributes:", [attr for attr in dir(gpiod) if not attr.startswith('_')])
    
    if hasattr(gpiod, 'line'):
        print("gpiod.line attributes:", [attr for attr in dir(gpiod.line) if not attr.startswith('_')])
    
    if hasattr(gpiod, 'line_settings'):
        print("gpiod.line_settings attributes:", [attr for attr in dir(gpiod.line_settings) if not attr.startswith('_')])
    
    print("Found Direction enum:", DIRECTION)
    if DIRECTION:
        print("Direction enum values:", [attr for attr in dir(DIRECTION) if not attr.startswith('_')])
    
    print("Found Value enum:", VALUE)
    if VALUE:
        print("Value enum values:", [attr for attr in dir(VALUE) if not attr.startswith('_')])
    print("=== End Debug ===")

def create_line_settings(direction_str):
    """Create LineSettings with proper direction"""
    if DIRECTION:
        if direction_str == "output":
            direction = DIRECTION.OUTPUT
        else:
            direction = DIRECTION.INPUT
        return gpiod.LineSettings(direction=direction)
    else:
        # Fallback: try creating with no direction specified
        return gpiod.LineSettings()

def check_button_generator():
    """
    Generator that yields button states continuously
    """
    try:
        with gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="button-led-demo",
            config={
                LED_PIN: create_line_settings("output"),
                BUTTON_PIN: create_line_settings("input")
            }
        ) as request:
            
            try:
                while True:
                    # Read button state
                    button_state = request.get_value(BUTTON_PIN)
                    
                    # Control LED based on button state
                    if VALUE:
                        # Use enum values if available
                        led_value = VALUE.ACTIVE if button_state else VALUE.INACTIVE
                        request.set_value(LED_PIN, led_value)
                    else:
                        # Use integer values as fallback
                        request.set_value(LED_PIN, 1 if button_state else 0)
                    
                    # Yield the button state (convert to int for consistency)
                    yield 1 if button_state else 0
                    
                    time.sleep(0.01)
                    
            except KeyboardInterrupt:
                request.set_value(LED_PIN, VALUE.INACTIVE if VALUE else 0)
                print("Button monitoring stopped")
            finally:
                # Turn off LED when done
                request.set_value(LED_PIN, VALUE.INACTIVE if VALUE else 0)
                
    except Exception as e:
        print(f"Error in check_button_generator: {e}")
        debug_enums()
        raise

def get_button_state():
    """
    Get current button state without infinite loop
    """
    try:
        with gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="button-reader",
            config={
                BUTTON_PIN: create_line_settings("input")
            }
        ) as request:
            button_state = request.get_value(BUTTON_PIN)
            return 1 if button_state else 0
    except Exception as e:
        print(f"Error in get_button_state: {e}")
        debug_enums()
        raise

def control_led(state):
    """
    Control LED state (True/1 = on, False/0 = off)
    """
    try:
        with gpiod.request_lines(
            "/dev/gpiochip0",
            consumer="led-control",
            config={
                LED_PIN: create_line_settings("output")
            }
        ) as request:
            if VALUE:
                led_value = VALUE.ACTIVE if state else VALUE.INACTIVE
                request.set_value(LED_PIN, led_value)
            else:
                request.set_value(LED_PIN, 1 if state else 0)
    except Exception as e:
        print(f"Error in control_led: {e}")
        debug_enums()
        raise

def wait_for_button_press():
    """
    Wait until button is pressed (returns when button goes from 0 to 1)
    """
    with gpiod.request_lines(
        "/dev/gpiochip0",
        consumer="button-waiter",
        config={
            BUTTON_PIN: create_line_settings("input")
        }
    ) as request:
        
        # Wait for button to be released first (if currently pressed)
        while request.get_value(BUTTON_PIN):
            time.sleep(0.01)
        
        # Wait for button press
        while not request.get_value(BUTTON_PIN):
            time.sleep(0.01)

def wait_for_button_release():
    """
    Wait until button is released (returns when button goes from 1 to 0)
    """
    with gpiod.request_lines(
        "/dev/gpiochip0",
        consumer="button-waiter",
        config={
            BUTTON_PIN: create_line_settings("input")
        }
    ) as request:
        
        # Wait for button release
        while request.get_value(BUTTON_PIN):
            time.sleep(0.01)

if __name__ == "__main__":
    debug_enums()
    try:
        control_led(True)
        time.sleep(1)
        control_led(False)
        print("LED test completed successfully!")
    except Exception as e:
        print(f"LED test failed: {e}")
    
    # Test button reading
    try:
        print("Press button to test...")
        wait_for_button_press()
        print("Button press detected!")
        control_led(True)
        wait_for_button_release()
        print("Button release detected!")
        control_led(False)
    except Exception as e:
        print(f"Button test failed: {e}")