"""
EE250 Lab 7: MCP3008 ADC + GPIO LED.
Modular helpers for re-use with any analog sensors (light, sound, etc.).
"""
import time
import sys
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

# --- ADC (MCP3008) helpers - re-usable for any analog sensor ---

def init_adc_hardware_spi(port=0, device=0):
    """Create and return an MCP3008 instance using hardware SPI."""
    return Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(port, device))


def init_adc_software_spi(clk=18, cs=25, miso=23, mosi=24):
    """Create and return an MCP3008 instance using software SPI (any GPIO pins)."""
    return Adafruit_MCP3008.MCP3008(clk=clk, cs=cs, miso=miso, mosi=mosi)


def read_adc_channel(mcp, channel):
    """Read one ADC channel (0-7). Returns 0-1023."""
    return mcp.read_adc(channel)


def read_adc_channels(mcp, channels):
    """Read multiple ADC channels. Returns list of values 0-1023. Re-use for any analog sensors."""
    return [mcp.read_adc(c) for c in channels]


# --- GPIO LED helpers (RPi.GPIO) ---

def setup_led(pin, mode=GPIO.BOARD):
    """Set GPIO pin as output for an LED. Use BOARD for physical pin numbers."""
    GPIO.setmode(mode)
    GPIO.setup(pin, GPIO.OUT)


def led_on(pin):
    """Turn LED on (HIGH)."""
    GPIO.output(pin, GPIO.HIGH)


def led_off(pin):
    """Turn LED off (LOW)."""
    GPIO.output(pin, GPIO.LOW)


def led_off(pin):
    """Turn LED off (LOW)."""
    GPIO.output(pin, GPIO.LOW)


def blink_led(pin, times, on_sec, off_sec):
    """Blink LED `times` times with given on/off intervals in seconds."""
    for _ in range(times):
        led_on(pin)
        time.sleep(on_sec)
        led_off(pin)
        time.sleep(off_sec)


def cleanup_gpio():
    """Release GPIO pins. Call on exit or Ctrl+C."""
    GPIO.cleanup()


# --- Configuration: set your sensor channels and thresholds here ---

LED_PIN = 11  # physical pin 11
SPI_PORT = 0
SPI_DEVICE = 0
LUX_CHANNEL = 0   # Grove light sensor
SOUND_CHANNEL = 1 # Grove sound sensor

# Set via experimentation (run calibration mode to find values):
LUX_THRESHOLD = 512    # above = bright, below = dark
SOUND_THRESHOLD = 512  # above = tap/loud


def run_adc_test(mcp, channels=None, interval=0.5):
    """
    Print ADC readings for all channels (or given list). Use this to find
    threshold values for light/dark and quiet/loud. Ctrl+C to stop.
    """
    channels = channels if channels is not None else list(range(8))
    print("Reading MCP3008 (Ctrl-C to quit). Channels:", channels)
    print("| " + " | ".join("CH{:d}".format(c) for c in channels) + " |")
    print("-" * (6 * len(channels) + len(channels) + 2))
    try:
        while True:
            values = read_adc_channels(mcp, channels)
            print("| " + " | ".join("{:4d}".format(v) for v in values) + " |")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")


def run_test_suite(mcp):
    """
    Test suite: run the following sequence in an infinite loop:
    1. Blink LED 5 times (500ms on / 500ms off)
    2. Read light sensor ~5s at 100ms, print raw + bright/dark
    3. Blink LED 4 times (200ms on / 200ms off)
    4. Read sound sensor ~5s at 100ms, print raw; on tap, LED on 100ms
    """
    interval_sec = 0.1
    duration_sec = 5.0
    n_samples = int(duration_sec / interval_sec)

    while True:
        # 1. Blink LED 5 times, 500ms on / 500ms off
        blink_led(LED_PIN, 5, 0.5, 0.5)

        # 2. Light sensor for ~5 seconds, 100ms intervals
        for _ in range(n_samples):
            raw = read_adc_channel(mcp, LUX_CHANNEL)
            label = "bright" if raw > LUX_THRESHOLD else "dark"
            print(raw, label)
            time.sleep(interval_sec)

        # 3. Blink LED 4 times, 200ms on / 200ms off
        blink_led(LED_PIN, 4, 0.2, 0.2)

        # 4. Sound sensor for ~5 seconds, 100ms intervals; on tap, LED on 100ms
        for _ in range(n_samples):
            raw = read_adc_channel(mcp, SOUND_CHANNEL)
            print(raw)
            if raw > SOUND_THRESHOLD:
                led_on(LED_PIN)
                time.sleep(0.1)
                led_off(LED_PIN)
            else:
                time.sleep(interval_sec)


def main():
    mcp = init_adc_hardware_spi(SPI_PORT, SPI_DEVICE)
    setup_led(LED_PIN)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "test":
        run_adc_test(mcp, channels=[LUX_CHANNEL, SOUND_CHANNEL])
        cleanup_gpio()
        return

    print("Test suite running (Ctrl-C to quit). Tune LUX_THRESHOLD and SOUND_THRESHOLD as needed.")
    try:
        run_test_suite(mcp)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        cleanup_gpio()


if __name__ == "__main__":
    main()
