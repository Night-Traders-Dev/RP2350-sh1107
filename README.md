# SH1107 OLED Display Controller with Keypad Interaction

## Overview

This project demonstrates a Python program to control an SH1107 OLED display using the CircuitPython `adafruit_displayio_sh1107` library. It includes features for displaying real-time system stats, uptime, RAM usage, and user interaction through buttons to toggle pages or reboot the system.

---

## Features

1. **System Stats Display**:
   - Shows CPU frequency and temperature of the microcontroller.

2. **Uptime Display**:
   - Displays the system uptime in `HH:MM:SS` format.

3. **RAM Stats Display**:
   - Displays the current RAM usage, including used, free, and total memory.

4. **Interactive Button Controls**:
   - **Button 0 (OLED_KEY0)**: 
     - Hold for 3 seconds to reboot the system.
     - Short press toggles between stats pages (CPU stats, uptime, and RAM stats).
   - **Button 1 (OLED_KEY1)**: 
     - Toggles the display between active and sleep modes.

5. **Status Bar**:
   - Provides context about the current mode (Stats, Uptime, or RAM).

6. **Dynamic Updates**:
   - Display content updates every second while automatically cycling between pages every 5 seconds.

---

## Installation

1. **CircuitPython Setup**:
   - Ensure your device supports CircuitPython and is correctly flashed with it.
   - Install the required libraries (`adafruit_displayio_sh1107`, `adafruit_display_text`, etc.) in the `lib` directory.

2. **Dependencies**:
   - `adafruit_displayio_sh1107`
   - `adafruit_display_text`
   - `busio`
   - `keypad`
   - `microcontroller`
   - `board`
   - `displayio`

3. **Connection**:
   - Connect your SH1107 OLED display and buttons as per the following pin mapping:

     | Pin         | Function               |
     |-------------|-----------------------|
     | GP8         | OLED_DC               |
     | GP9         | OLED_CS               |
     | GP10        | OLED_CLK              |
     | GP11        | OLED_DIN              |
     | GP12        | OLED_RST              |
     | GP15        | Button 0 (OLED_KEY0)  |
     | GP17        | Button 1 (OLED_KEY1)  |

4. **Deploy Code**:
   - Copy the Python script to your CircuitPython device.

---

## Usage

### Button Functions
- **Button 0 (Reboot/Toggle)**:
  - Hold for 3 seconds: Reboots the device.
  - Short press: Toggles between the stats pages (CPU stats, uptime, and RAM).

- **Button 1 (Display Sleep/Wake)**:
  - Toggles the display between sleep and active states.

### Display Modes
1. **CPU Stats Page**:
   - Displays CPU frequency and temperature for the system.
   - Example:
     ```
     CPU Stats
     120.0/120.0 Mhz
     32.50/33.00 C
     ```

2. **Uptime Page**:
   - Shows the elapsed time since the system booted.
   - Example:
     ```
     Uptime Stats
     00:10:15
     ```

3. **RAM Stats Page**:
   - Displays the current RAM usage, including used, free, and total memory.
   - Example:
     ```
     RAM Stats
     Used: 2048 bytes
     Free: 4096 bytes
     Total: 6144 bytes
     ```

---

## Known Issues

- **`rotate_display`**:
  - Currently not functional due to incomplete implementation of SPI commands.
  - Requires proper use of the `send_command` function to send SH1107 commands.

- **`invert_display`**:
  - Inversion functionality is not working as intended. Needs correct handling of display controller commands.

- **`send_command`**:
  - Low-level SPI commands require proper debugging and implementation to communicate with the SH1107 controller directly.

---

## Future Improvements

1. **Fix `rotate_display` and `invert_display` Functions**:
   - Properly send SPI commands for display inversion and rotation.

2. **Optimize Key Event Handling**:
   - Improve responsiveness and debouncing for button presses.

3. **Add More Stats**:
   - Include additional system metrics like power state or sensor data.

4. **Enhanced Graphics**:
   - Add animations or visual separators between sections.

---

## Contributing

Contributions, bug reports, and feature requests are welcome! Please submit issues or pull requests on the project's repository.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- Adafruit CircuitPython Libraries
- SH1107 OLED Datasheet
