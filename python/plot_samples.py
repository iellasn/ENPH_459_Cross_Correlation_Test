import serial
import matplotlib.pyplot as plt
import numpy as np

# Config
PORT = '/dev/cu.usbserial-14420'
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
print(f"Got {len(samples)} samples")

# Plot
plt.figure(figsize=(12, 4))
plt.plot(samples)
plt.title("ESP32 ADC Raw Samples")
plt.xlabel("Sample index")
plt.ylabel("ADC value (0-4095)")
plt.grid(True)
plt.show()