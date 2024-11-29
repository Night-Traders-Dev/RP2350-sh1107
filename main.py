from adafruit_display_text import bitmap_label as label
import adafruit_displayio_sh1107
import board
import busio
import displayio
import gc
import keypad
import microcontroller
import sys
import terminalio
import time

OLED_DC = board.GP8
OLED_CS = board.GP9
OLED_CLK = board.GP10
OLED_DIN = board.GP11
OLED_RST = board.GP12
OLED_KEY0 = board.GP15
OLED_KEY1 = board.GP17

WIDTH = 128
HEIGHT = 64
BORDER = 2
blk_hex = 0x000000
wht_hex = 0xFFFFFF


def rotate_display(rotation):
    """Rotate the display to 0, 90, 180, or 270 degrees."""
    if rotation == 0:
        send_command(0xA0)  # Default segment remap
        send_command(0xC0)  # Default COM scan direction
    elif rotation == 90:
        send_command(0xA1)  # Horizontal flip
        send_command(0xC0)  # Default COM scan direction
    elif rotation == 180:
        send_command(0xA0)  # Default segment remap
        send_command(0xC8)  # Vertical flip
    elif rotation == 270:
        send_command(0xA1)  # Horizontal flip
        send_command(0xC8)  # Vertical flip
        
def invert_display(invert):
    """Invert the display colors."""
    if invert:
        send_command(0xA7)  # Invert display
    else:
        send_command(0xA6)  # Normal display
        
# Function to send a command using FourWire.send
def send_command(command, data=None):
    """Send a command and optional data to the SH1107 display."""
#    b = bytearray(2)
#    b[0] = command
#    b[1] = 0x00
    # Send the command byte
    spi_bus.try_lock()
    spi_bus.configure(baudrate=5000000, phase=0, polarity=0)
    spi_bus.write(bytearray(command))
    spi_bus.unlock()
    # Send any data bytes, if provided
    if data:
        display_bus.send(True, bytes(data))

def draw_bg():
    color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
    color_palette = displayio.Palette(1)
    color_palette[0] = blk_hex
    bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)


def draw_text(init_text, x, y):
    text_area = label.Label(terminalio.FONT, text=init_text, color=wht_hex, scale=1)
    text_area.x = x
    text_area.y = y
    splash.append(text_area)


def update_text(new_text, x, y):
    while len(splash) > 1:
        splash.pop()
    new_text_area = label.Label(terminalio.FONT, text=new_text, color=wht_hex, scale=1)
    new_text_area.x = x
    new_text_area.y = y
    splash.append(new_text_area)

def draw_separator():
    separator = displayio.Bitmap(WIDTH, 1, 1)
    separator_palette = displayio.Palette(1)
    separator_palette[0] = blk_hex
    separator_sprite = displayio.TileGrid(separator, pixel_shader=separator_palette, x=0, y=12)
    splash.insert(1, separator_sprite)


def draw_status_bar(status_text):
    while len(splash) > 1:
        splash.pop(0)
    status_bg = displayio.Bitmap(WIDTH, 12, 1)
    status_palette = displayio.Palette(1)
    status_palette[0] = wht_hex
    status_bg_sprite = displayio.TileGrid(status_bg, pixel_shader=status_palette, x=0, y=0)
    splash.insert(0, status_bg_sprite)
    status_text_area = label.Label(terminalio.FONT, text=status_text, color=blk_hex, scale=1)
    status_text_area.x = 2  # Padding from the left
    status_text_area.y = 4  # Padding from the top
    splash.insert(1, status_text_area)

def get_cpu_stats():
    cpufreq0 = microcontroller.cpus[0].frequency / 1_000_000
    cpufreq1 = microcontroller.cpus[1].frequency / 1_000_000
    cputemp0 = microcontroller.cpus[0].temperature
    cputemp1 = microcontroller.cpus[1].temperature
    return f"{cpufreq0}/{cpufreq1} Mhz\n{cputemp0:,.2f}/{cputemp1:,.2f} C"


def get_uptime():
    uptime_seconds = time.monotonic()
    minutes, seconds = divmod(int(uptime_seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def boot_man():
    draw_text("Kraken Machine", x=10, y=20)
    draw_text(f"Heap: {gc.mem_alloc()} bytes", x=10, y=30)
    draw_text(f"Heap: {gc.mem_free()} bytes", x=10, y=40)
    sys_platform = sys.platform
    time.sleep(0.5)
    update_text(f"Board: {sys_platform}", x=10, y=20)
    time.sleep(1)
    
# Initialize display
displayio.release_displays()
spi_bus = busio.SPI(OLED_CLK, OLED_DIN)
display_bus = displayio.FourWire(spi_bus, command=OLED_DC, chip_select=OLED_CS, reset=OLED_RST)
display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT)
splash = displayio.Group()
display.root_group = splash
draw_bg()

last_update_time = time.monotonic()
last_toggle_time = time.monotonic() 
keys = keypad.Keys((OLED_KEY0, OLED_KEY1), value_when_pressed=False, pull=True)
reboot_message_active = False
toggle_display = True
button_hold_start = None
hold_duration_required = 3

boot_man()

while True:
    time.sleep(0.1)
    gc.collect()
    event = keys.events.get()
    if event:
        if event.pressed:
            if event.key_number == 0:
                button_hold_start = time.monotonic()
            elif event.key_number == 1:
                if display.is_awake:
                    display.sleep()
                else:
                    display.wake()
                time.sleep(0.1)

        elif event.released and event.key_number == 0:
            if button_hold_start is not None:
                hold_duration = time.monotonic() - button_hold_start
                if hold_duration >= hold_duration_required:
                    update_text("Rebooting...", x=10, y=20)
                    draw_status_bar(f"Kraken Machine")
                    time.sleep(0.5)
                    microcontroller.reset()
                else:
                    toggle_display = not toggle_display
                    button_hold_start = None

    current_time = time.monotonic()

    if current_time - last_toggle_time >= 5 and not reboot_message_active:
        toggle_display = not toggle_display
        last_toggle_time = current_time

    if current_time - last_update_time >= 1 and not reboot_message_active:
        if toggle_display:
            cpudata = get_cpu_stats()
            update_text(f"{cpudata}", x=20, y=25)
            sys_platform = sys.platform
            draw_status_bar(f"{sys_platform} Stats")
        else:
            uptime = get_uptime()
            update_text(f"{uptime}", x=40, y=25)
            draw_status_bar("Uptime Stats")
        last_update_time = current_time
