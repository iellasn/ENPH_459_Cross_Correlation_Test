import serial
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# =================================================================
# CONFIGURATION — match to your setup
# =================================================================
PORT = '/dev/cu.usbserial-14320'  # update if needed
BAUD = 115200
NUM_SAMPLES = 1024
FS = 100000        # ESP32 sample rate (Hz)
F_CENTER = 40000   # 40 kHz
CYCLES = 8         # burst length to test

# =================================================================
# STEP 1 — Read real signal from ESP32
# =================================================================
print("Reading samples from ESP32...")
ser = serial.Serial(PORT, BAUD, timeout=5)

rx_signal = []
while len(rx_signal) < NUM_SAMPLES:
    line = ser.readline().decode('utf-8').strip()
    if line.isdigit():
        rx_signal.append(int(line))

ser.close()
rx_signal = np.array(rx_signal, dtype=float)

# Normalize to -1 to 1 (remove DC bias, scale)
rx_signal = rx_signal - np.mean(rx_signal)
rx_signal = rx_signal / (np.max(np.abs(rx_signal)) + 1e-12)

print(f"Got {len(rx_signal)} samples")

# =================================================================
# STEP 2 — Generate clean reference template
# (same burst the transmitter sends)
# =================================================================
def generate_burst(fs, f_center, cycles):
    t_burst = np.arange(0, cycles / f_center, 1 / fs)
    sig = np.sin(2 * np.pi * f_center * t_burst)
    sig *= signal.windows.hann(len(sig))  # smooth edges
    return sig

tx_pulse = generate_burst(FS, F_CENTER, CYCLES)
print(f"Template length: {len(tx_pulse)} samples ({CYCLES} cycles)")

# =================================================================
# STEP 3 — Three correlation methods (from Lydia's framework)
# =================================================================
def compute_correlation(sig_rx, sig_tx, method='CC'):
    n_fft = 2 ** int(np.ceil(np.log2(len(sig_rx) + len(sig_tx))))
    X_rx = np.fft.fft(sig_rx, n=n_fft)
    X_tx = np.fft.fft(sig_tx, n=n_fft)
    cpsd = X_rx * np.conj(X_tx)

    if method == 'CC':
        weight = 1.0
    elif method == 'GCC':
        weight = 1.0 / (np.abs(X_rx) ** 2 + 1e-9)
    elif method == 'GCC-PHAT':
        weight = 1.0 / (np.abs(cpsd) + 1e-9)

    res = np.real(np.fft.ifft(cpsd * weight))
    return res

methods = ['CC', 'GCC', 'GCC-PHAT']

# =================================================================
# STEP 4 — Plot
# =================================================================
fig, axes = plt.subplots(3, 1, figsize=(14, 10))
fig.suptitle(f"Hardware Cross-Correlation Test\n"
             f"ESP32 @ {FS/1000:.0f} kSPS | {CYCLES}-cycle burst template | "
             f"{len(tx_pulse)} samples", fontsize=13)

for ax, method in zip(axes, methods):
    corr = compute_correlation(rx_signal, tx_pulse, method=method)
    corr_norm = np.abs(corr) / (np.max(np.abs(corr)) + 1e-12)

    peak_idx = np.argmax(corr_norm)
    lags = np.arange(len(corr))

    ax.plot(lags, corr_norm, lw=1)
    ax.axvline(peak_idx, color='r', linestyle='--',
               label=f"Peak at sample {peak_idx}")
    ax.set_ylabel("Normalised correlation")
    ax.set_title(method)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

axes[-1].set_xlabel("Lag (samples)")
plt.tight_layout()
plt.show()

# =================================================================
# STEP 5 — Print summary
# =================================================================
print("\n" + "="*55)
print(f"{'Method':<12} | {'Peak index':<12} | {'Peak value'}")
print("-"*55)
for method in methods:
    corr = compute_correlation(rx_signal, tx_pulse, method=method)
    corr_norm = np.abs(corr) / (np.max(np.abs(corr)) + 1e-12)
    peak_idx = np.argmax(corr_norm)
    second_peak = np.max(np.delete(corr_norm,
                  range(max(0, peak_idx-10), min(len(corr_norm), peak_idx+10))))
    print(f"{method:<12} | {peak_idx:<12} | "
          f"peak/sidelobe ratio = {1.0/second_peak:.2f}x")
print("="*55)