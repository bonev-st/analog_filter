# Author: Stanimir Bonev
# Description: Generates synthetic step-signal data and plots all three filter outputs for comparison

import pandas as pd
import matplotlib.pyplot as plt
from filters import EMAFilter, RMSFilter, AsymmetricFilter

# --- Synthetic sensor data parameters ---
TIME_STEP_MS    = 100          # milliseconds between samples
TOTAL_TIME_MS   = 4000         # total signal duration in milliseconds
VALUE_HIGH      = 100.0        # high level of the step signal
VALUE_LOW       = 25.0         # low level of the step signal
# Transition times (seconds): low→high, high→low, low→high, high→low ...
TRANSITIONS     = [2.0, 4.0, 10.0, 15.0]

# --- Filter parameters ---
EMA_ALPHA       = 0.25         # single smoothing factor for EMAFilter
RMS_ALPHA       = 0.25         # same alpha for RMSFilter comparison
ASYM_ALPHA_UP   = 0.05         # slow rise
ASYM_ALPHA_DOWN = 0.005        # very slow fall

# --- Generate synthetic step signal ---
data = {"Time": [], "Value": []}

for i in range(0, TOTAL_TIME_MS, TIME_STEP_MS):
    sec = i / 1000
    data["Time"].append(sec)
    # Count how many transition boundaries have been crossed; start at VALUE_HIGH
    num_transitions = sum(1 for t in TRANSITIONS if sec >= t)
    value = VALUE_LOW if num_transitions % 2 == 1 else VALUE_HIGH
    data["Value"].append(value)

df = pd.DataFrame(data)

# --- Apply filters ---
df["EMA"]        = df["Value"].apply(EMAFilter(EMA_ALPHA, VALUE_LOW).update)
df["RMS"]        = df["Value"].apply(RMSFilter(RMS_ALPHA, VALUE_LOW).update)
df["Asymmetric"] = df["Value"].apply(
    AsymmetricFilter(ASYM_ALPHA_UP, ASYM_ALPHA_DOWN, VALUE_LOW).update
)

# --- Plot ---
plt.figure()
plt.plot(df["Time"], df["Value"],      label="Input")
plt.plot(df["Time"], df["EMA"],        label="EMA")
plt.plot(df["Time"], df["RMS"],        label="RMS")
plt.plot(df["Time"], df["Asymmetric"], label="Asymmetric")
plt.xlabel("Time (s)")
plt.ylabel("Value")
plt.title("Analog Filter Comparison")
plt.legend()
plt.show()
