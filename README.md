# ENPH 459 Cross Correlation Test

ESP32-based ADC sampling pipeline for TDOA (Time Difference of Arrival) research. Samples an analog signal via DMA at 83,333 Hz and streams data over serial to a Python plotting script.

---

## Hardware Requirements

- ESP32 Pico Kit (pico32)
- USB-A to Micro-USB cable
- Analog signal source (e.g. function generator) connected to **GPIO36**
- Signal must be 0–3.3V (do not exceed 3.3V)

---

## Software Requirements

- macOS
- [VS Code](https://code.visualstudio.com/)
- [PlatformIO IDE extension for VS Code](https://platformio.org/install/ide?install=vscode)
- Python 3 (via Anaconda or Homebrew)
- Python packages: `pyserial`, `matplotlib`, `numpy`

---

## Setup

### 1. Install dependencies

Install Python packages if you haven't already:

```bash
pip install pyserial matplotlib numpy
```

### 2. Clone the repository

```bash
git clone https://github.com/iellasn/ENPH_459_Cross_Correlation_Test.git
cd ENPH_459_Cross_Correlation_Test
```

### 3. Open in VS Code

```bash
code .
```

PlatformIO will automatically detect the `platformio.ini` and configure the project.

---

## Flashing the ESP32

### 1. Connect the ESP32

Plug the ESP32 Pico Kit into your Mac via USB. Check it appears as a serial device:

```bash
ls /dev/cu.*
```

You should see something like `/dev/cu.usbserial-14420`. If the port is different, update `upload_port` and `monitor_port` in `platformio.ini`.

### 2. Flash the firmware

In VS Code, click the **→ Upload** button in the PlatformIO toolbar at the bottom, or run:

```bash
pio run --target upload
```

Wait for:
```
Hash of data verified.
Hard resetting via RTS pin...
====== [SUCCESS] ======
```

> **Note:** If the upload fails, hold the **BOOT** button on the ESP32, press **EN** (reset), release **BOOT**, then try uploading again.

---

## Running the Python Script

> **Important:** The PlatformIO serial monitor and the Python script cannot be open at the same time — they both need exclusive access to the serial port. Close the PlatformIO monitor before running Python.

### 1. Press EN on the ESP32

Press the **EN** (reset) button on the board. The firmware will sample 1024 points and wait 2 seconds before sending data.

### 2. Immediately run the script

```bash
cd python
python plot_samples.py
```

You have ~2 seconds after pressing EN before the data transmits. The script will print each received value and display two plots:

- **Top**: raw ADC samples (0–4095) vs sample index
- **Bottom**: FFT showing frequency content of the signal

---

## How It Works

### Firmware (`src/main.c`)

The ESP32 uses the ESP-IDF `adc_continuous` driver to sample GPIO36 via DMA at 83,333 Hz. A hardware timer triggers the ADC 83,333 times per second — the CPU is not involved in timing. Each 4-byte DMA result contains a 12-bit ADC value (0–4095) and the channel number. Results are collected in batches of 256 into a ring buffer in RAM, then unpacked into a `samples[]` array. Once 1024 samples are collected, they are printed over UART framed with `START` and `END` markers.

### Python (`python/plot_samples.py`)

Opens the serial port, waits for the `START` marker, reads integers until `END`, then plots the time-domain signal and its FFT using matplotlib.

---

## Key Parameters

| Parameter | Value | Notes |
|---|---|---|
| Sample rate | 83,333 Hz | Maximum supported by ESP-IDF `adc_continuous` API |
| ADC resolution | 12-bit | Values 0–4095 |
| Samples per capture | 1024 | ~12ms window |
| ADC pin | GPIO36 | ADC1 Channel 0 |
| Baud rate | 115200 | UART to laptop |

---

## Troubleshooting

**Python hangs at startup**
- Close the PlatformIO serial monitor first
- Press EN on the ESP32, then immediately run the Python script

**`device disconnected or multiple access on port`**
- Another process (PlatformIO monitor) is holding the serial port open. Close it.

**No samples received / script times out**
- Check the USB cable is data-capable (not charge-only)
- Verify the port in `plot_samples.py` matches your device: `ls /dev/cu.*`
- Re-flash the firmware

**Upload fails**
- Enter download mode manually: hold BOOT, press EN, release BOOT, then upload
