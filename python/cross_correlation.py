import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate

# Config
PORT = '/dev/cu.usbserial-14320'  # update if needed
BAUD = 115200
NUM_SAMPLES = 1024

# Read samples from ESP32
ser = serial.Serial(PORT, BAUD, timeout=5)
print("Reading samples...")

samples = []
while len(samples) < NUM_SAMPLES:
    line = ser.readline().decode('utf-8').strip()
    if line.isdigit():
        samples.append(int(line))

ser.close()

signal = np.array(samples, dtype=float)

# Artificially shift the signal to simulate a second receiver
SHIFT = 50  # samples — this is your known fake TDOA
signal_delayed = np.roll(signal, SHIFT)

# Cross-correlate
correlation = correlate(signal, signal_delayed, mode='full')
lags = np.arange(-len(signal) + 1, len(signal))

# Find peak
peak_lag = lags[np.argmax(correlation)]
print(f"Known shift: {SHIFT} samples")
print(f"Detected lag: {peak_lag} samples")
print(f"Match: {abs(peak_lag) == SHIFT}")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(12, 8))

axes[0].plot(signal)
axes[0].set_title("Signal 1 (original)")
axes[0].set_ylabel("ADC value")

axes[1].plot(signal_delayed)
axes[1].set_title(f"Signal 2 (shifted by {SHIFT} samples)")
axes[1].set_ylabel("ADC value")

axes[2].plot(lags, correlation)
axes[2].axvline(peak_lag, color='r', linestyle='--', label=f"Peak at lag={peak_lag}")
axes[2].set_title("Cross-Correlation")
axes[2].set_xlabel("Lag (samples)")
axes[2].set_ylabel("Correlation")
axes[2].legend()

plt.tight_layout()
plt.show()