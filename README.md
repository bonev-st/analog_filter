# Analog Filter Tool — `filter.py`

This tool shows how a **low-pass filter** works. Imagine you are measuring temperature with a sensor,
but the numbers jump around a lot — up, down, up, down — even when nothing really changed.
A low-pass filter is like a calm friend who says:
*"Don't overreact. Let's take it slow and smooth things out."*

---

## What Does the Script Do?

1. It makes up some pretend sensor data that jumps between two values (like 100 and 25).
2. It runs that noisy data through a filter.
3. It draws a picture (a plot) so you can see how the filter smooths the jumps.

---

## Step 1 — Install Python on Windows 11

Python is the language the script is written in. Think of it as teaching your computer a new language.

1. Open your web browser and go to **https://www.python.org/downloads/**
2. Click the big yellow button that says **"Download Python 3.x.x"**
3. Open the downloaded file (it ends in `.exe`)
4. **IMPORTANT** — on the first screen of the installer, tick the box that says **"Add python.exe to PATH"**
   (this lets Windows find Python from anywhere)
5. Click **"Install Now"** and wait for it to finish
6. Click **"Close"**

To check it worked, open **PowerShell** (press `Win + R`, type `powershell`, press Enter) and type:

```
python --version
```

You should see something like `Python 3.12.4`.

---

## Step 2 — Get the Project Files

Open **PowerShell** and go to the folder where the project lives:

```
cd "C:\W1\git\ModularHighPowerSystem\SW\MCU\MOD-5544-060(IR_Sensor)\tools\analog_filter"
```

---

## Step 3 — Create a Virtual Environment

A virtual environment is like a **lunchbox just for this project**.
It keeps all the tools this project needs inside its own box, so they do not mix with other projects.

In PowerShell, run:

```
python -m venv .venv
```

This creates a hidden folder called `.venv` in the project directory.

Now **activate** the lunchbox (tell Windows to use it):

```
.venv\Scripts\activate
```

Your PowerShell prompt will change and show `(.venv)` at the start — that means it is active!

---

## Step 4 — Install the Required Packages

The script needs two helper libraries:

| Package | What it does |
|---|---|
| `pandas` | Organises data into a table (like a spreadsheet) |
| `matplotlib` | Draws charts and plots |

Install them with one command:

```
pip install -r requirements.txt
```

pip is Python's shopping assistant — it goes and fetches the packages for you.

---

## Step 5 — Run the Script

```
python demo.py
```

A window will pop up showing two lines:
- **Blue line** — the original noisy data (jumps sharply between 100 and 25)
- **Orange line** — the filtered data (changes slowly and smoothly)

---

## Understanding `filter.py` — Line by Line

```python
import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt
```
We bring in our helper tools: `pandas` for the data table, `matplotlib` for drawing, and `sqrt` (square root) from Python's built-in math box.

---

```python
data = {"Time": [], "Value": []}

for i in range(0, 4000, 100):
    sec = i / 1000
    data["Time"].append(sec)
    if sec < 2:
        data["Value"].append(100.0)
    elif sec < 4:
        data["Value"].append(25.0)
    elif sec < 10:
        data["Value"].append(100.0)
    elif sec < 15:
        data["Value"].append(25.0)
    else:
        data["Value"].append(100.0)
```
This is our pretend sensor. It produces time steps from 0 to 3.9 seconds (every 0.1 s) and switches the value between 100 and 25 at specific times — like a light switch being flipped.

```python
df = pd.DataFrame(data)
```
We put all those numbers into a pandas table (called a DataFrame) so they are easy to work with.

---

### The Filters

#### `filter` — Basic Exponential (EMA)

```python
class filter:
    def __init__(self, alpha, init):
        self.alpha = alpha
        self.value = init

    def update(self, value):
        self.value = self.alpha * value + (1 - self.alpha) * self.value
        return self.value
```

This is the **simplest and most common** filter. It is called an **Exponential Moving Average (EMA)**.

Think of it like steering a heavy boat:
- `alpha` is how hard you can turn the wheel. A big alpha (close to 1) = fast reaction. A small alpha (close to 0) = very slow, very smooth.
- Every update it takes a little bit of the new reading and mixes it with what it remembered before.

**Formula:** `new = alpha × input + (1 − alpha) × previous`

With `alpha = 0.25` it takes about 4 updates to get halfway to a new value.

---

#### `filter1` — RMS Exponential

```python
class filter1:
    def __init__(self, alpha):
        self.alpha = alpha
        self.value = 0.0

    def update(self, value):
        self.value = sqrt(self.alpha * (value**2) + (1 - self.alpha) * (self.value**2))
        return self.value
```

Same idea as the basic filter, but it works on **squared values** and takes a square root at the end.
This is useful when you care about the **power** of a signal (like measuring AC voltage or vibration energy) rather than its plain average.

---

#### `filter2` — Asymmetric EMA (different speed up vs. down)

```python
class filter2:
    def __init__(self, alpha_up, alpha_down):
        self.alpha_up = alpha_up
        self.alpha_down = alpha_down
        self.value = 0.0

    def update(self, value):
        alpha = self.alpha_up if value > self.value else self.alpha_down
        self.value = alpha * value + (1 - alpha) * self.value
        return self.value
```

This filter reacts **faster when the value goes up** than when it comes down (or the other way around — you choose).

Real-world example: a battery charge indicator.
You want it to show a drop quickly (so the user knows), but rise slowly (so it does not flicker back and forth).
- `alpha_up = 0.05` — rises slowly
- `alpha_down = 0.005` — falls very slowly

---

### Running the Filters and Plotting

```python
alpha = 0.25
f = filter(alpha, 25.0)     # start the filter at 25

df["Value_Filtered"] = df["Value"].apply(f.update)
```

We create a filter object and run every row of the data table through it one by one.
The result is stored as a new column called `Value_Filtered`.

```python
plt.figure()
plt.plot(df["Time"], df["Value"], label="Input Data")
plt.plot(df["Time"], df["Value_Filtered"], label="Filtered Data")
plt.xlabel("Time")
plt.ylabel("Value")
plt.legend()
plt.show()
```

Finally we draw the chart. `plt.show()` opens a window with the plot.

---

## File Structure

```
analog_filter/
├── filters.py     ← EMAFilter, RMSFilter, AsymmetricFilter (importable library)
├── demo.py        ← synthetic data generation and comparison plot
├── requirements.txt
└── README.md
```
