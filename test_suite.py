import time
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# --- Pin & SPI configuration (matches starter) ---
LED_PIN    = 11   # physical pin 11 (BOARD mode)
SPI_PORT   = 0
SPI_DEVICE = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# --- Sensor channels ---
LUX_CHANNEL   = 0   # Grove light sensor on CH0
SOUND_CHANNEL = 1   # Grove sound sensor on CH1

# Set these by running the script and observing printed values:
# cover the light sensor with your hand → note the "dark" reading
# tap the sound sensor → note the "loud" reading
LUX_THRESHOLD   = 15   # below = dark, above = bright (adjust via experimentation)
SOUND_THRESHOLD = 20   # above = tap detected        (adjust via experimentation)


# --- Modular LED helpers ---

def led_on():
    GPIO.output(LED_PIN, GPIO.HIGH)

def led_off():
    GPIO.output(LED_PIN, GPIO.LOW)

def blink_led(times, on_ms, off_ms):
    """Blink LED a given number of times with on/off intervals in milliseconds."""
    for _ in range(times):
        led_on()
        time.sleep(on_ms / 1000.0)
        led_off()
        time.sleep(off_ms / 1000.0)


# --- Modular ADC helpers (re-usable for any analog sensor) ---

def read_channel(channel):
    """Read a single MCP3008 channel (0-7). Returns 0-1023."""
    return mcp.read_adc(channel)

def read_channels(channels):
    """Read multiple MCP3008 channels. Returns list of 0-1023 values."""
    return [mcp.read_adc(c) for c in channels]


# --- Test suite steps ---

def step_light_sensor(duration_s=5.0, interval_ms=100):
    """Read light sensor for ~duration_s seconds, print raw value and bright/dark label."""
    n = int(duration_s / (interval_ms / 1000.0))
    for _ in range(n):
        raw = read_channel(LUX_CHANNEL)
        label = "bright" if raw > LUX_THRESHOLD else "dark"
        print("light:", raw, label)
        time.sleep(interval_ms / 1000.0)

def step_sound_sensor(duration_s=5.0, interval_ms=100):
    """Read sound sensor for ~duration_s seconds. Flash LED 100ms on tap. Keeps strict 100ms cadence."""
    n = int(duration_s / (interval_ms / 1000.0))
    for _ in range(n):
        start = time.time()
        raw = read_channel(SOUND_CHANNEL)
        print("sound:", raw)
        if raw > SOUND_THRESHOLD:
            led_on()
            time.sleep(0.1)
            led_off()
        elapsed = time.time() - start
        remaining = (interval_ms / 1000.0) - elapsed
        if remaining > 0:
            time.sleep(remaining)


# --- Main test loop ---

print("Test suite running. Ctrl-C to stop.")
print("Thresholds: light={}, sound={}".format(LUX_THRESHOLD, SOUND_THRESHOLD))

try:
    while True:
        # 1. Blink LED 5 times, 500ms on / 500ms off
        print("\n[1] Blink x5 (500ms)")
        blink_led(5, 500, 500)

        # 2. Read light sensor ~5s at 100ms intervals
        print("[2] Light sensor (5s)")
        step_light_sensor()

        # 3. Blink LED 4 times, 200ms on / 200ms off
        print("[3] Blink x4 (200ms)")
        blink_led(4, 200, 200)

        # 4. Read sound sensor ~5s at 100ms intervals; LED on tap
        print("[4] Sound sensor (5s)")
        step_sound_sensor()

except KeyboardInterrupt:
    print("\nStopped.")
finally:
    GPIO.cleanup()
