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


def get_cpu_stats():
    cpufreq0 = microcontroller.cpus[0].frequency / 1_000_000
    cpufreq1 = microcontroller.cpus[1].frequency / 1_000_000
    cputemp0 = microcontroller.cpus[0].temperature
    cputemp1 = microcontroller.cpus[1].temperature
    return f"CPU Stats\n{cpufreq0}/{cpufreq1} Mhz\n{cputemp0:,.2f}/{cputemp1:,.2f} C"

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
keys = keypad.Keys((OLED_KEY0, OLED_KEY1), value_when_pressed=False, pull=True)
reboot_message_active = False

boot_man()
while True:
    time.sleep(0.1)
    gc.collect()
    event = keys.events.get()
    if event:
        if event.pressed:
            if event.key_number == 0:
                update_text("Rebooting...", x=10, y=20)
                reboot_message_active = True
                time.sleep(0.5)
                microcontroller.reset()
            elif event.key_number == 1:
                if display.is_awake:
                    display.sleep()
                else:
                    display.wake()
                time.sleep(0.1)

    current_time = time.monotonic()
    if current_time - last_update_time >= 1 and not reboot_message_active:
        cpudata = get_cpu_stats()
        update_text(f"{cpudata}", x=10, y=20)
        last_update_time = current_time
