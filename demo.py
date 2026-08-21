# Author: Stanimir Bonev
# Description: Generates synthetic step-signal data and plots all three filter outputs for comparison
"""Generate a synthetic step signal and compare the EMA, RMS and asymmetric filters."""

import argparse
import os
import sys

import matplotlib
import pandas as pd

from filters import EMAFilter, RMSFilter, AsymmetricFilter

DEFAULT_OUTPUT = "analog_filter.png"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output",
        nargs="?", const=DEFAULT_OUTPUT, default=None, metavar="PATH",
        help=f"write the plot to an image file instead of opening a window "
             f"(default file name: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def have_display() -> bool:
    """True if a GUI session is available to open a plot window."""
    if sys.platform.startswith("win") or sys.platform == "darwin":
        return True
    # Linux/BSD: a window needs an X11 or Wayland session.
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


args = parse_args()

# Pick the drawing backend *before* importing pyplot. On a headless Linux box
# (SSH session, container, WSL without an X server) there is no window system,
# so fall back to the file-writing "Agg" backend instead of failing.
interactive = args.output is None and have_display()
if not interactive:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (must follow matplotlib.use)

if interactive and plt.get_backend().lower() == "agg":
    # matplotlib found no GUI toolkit (e.g. python3-tk not installed).
    interactive = False

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
plt.tight_layout()

if interactive:
    plt.show()
else:
    output = args.output or DEFAULT_OUTPUT
    plt.savefig(output, dpi=150)
    if args.output is None:
        print("No interactive display available.")
        if have_display():
            # A GUI session exists but matplotlib has no toolkit to draw with.
            print("Tip: install a GUI backend for a window instead, e.g. "
                  "sudo apt install python3-tk")
    print(f"Plot written to {os.path.abspath(output)}")
