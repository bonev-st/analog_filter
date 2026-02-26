# Analog Filter Tool — `filters.py` + `demo.py`

This tool shows how **low-pass filters** work. Imagine you are measuring temperature with a sensor,
but the numbers jump around a lot — up, down, up, down — even when nothing really changed.
A low-pass filter is like a calm friend who says:
*"Don't overreact. Let's take it slow and smooth things out."*

---

## What Does the Script Do?

1. It makes up some pretend sensor data that jumps between two values (like 100 and 25).
2. It runs that data through **three different filters** at the same time.
3. It draws a picture (a plot) so you can compare how each filter smooths the jumps differently.

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

```bash
python --version
```

You should see something like `Python 3.12.4`.

---

## Step 2 — Get the Project Files

Open **PowerShell** and go to the folder where the project lives:

```bash
cd "<git_repo>\analog_filter"
```

---

## Step 3 — Create a Virtual Environment

A virtual environment is like a **lunchbox just for this project**.
It keeps all the tools this project needs inside its own box, so they do not mix with other projects.

In PowerShell, run:

```bash
python -m venv .venv
```

This creates a hidden folder called `.venv` in the project directory.

Now **activate** the lunchbox (tell Windows to use it):

```bash
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

```bash
pip install -r requirements.txt
```

pip is Python's shopping assistant — it goes and fetches the packages for you.

---

## Step 5 — Run the Script

```bash
python demo.py
```

A window will pop up showing four lines:
- **Blue line** — the original data (jumps sharply between 100 and 25)
- **Orange line** — EMA filtered (smooths the jumps evenly)
- **Green line** — RMS filtered (smooths signal power, always stays positive)
- **Red line** — Asymmetric filtered (rises slowly, falls very slowly)

---

## Step 6 — Run the Tests

The filter classes have a suite of unit tests that you can run any time to verify everything works correctly.
No extra packages are needed — Python's built-in `unittest` module is used.

```bash
python -m unittest test_filters -v
```

You should see 29 lines ending in `ok` and a final summary:

```bash
----------------------------------------------------------------------
Ran 29 tests in 0.001s

OK
```

The tests check:

| Filter | What is tested |
|---|---|
| `EMAFilter` | Construction, alpha boundary values, formula correctness, state persistence, convergence |
| `RMSFilter` | Same as above, plus output is always non-negative |
| `AsymmetricFilter` | Separate `ValueError` guards for both alphas, correct alpha selection on rise vs. fall, asymmetric speed behaviour |

---

## Understanding the Code

The project is split into three files:

| File | Purpose |
|---|---|
| `filters.py` | The filter classes — can be imported by any project |
| `demo.py` | Generates test data, applies all three filters, and plots the result |
| `test_filters.py` | Unit tests for all three filter classes |

---

### `filters.py` — The Filter Library

```python
from math import sqrt
```
The only import needed — pure Python, no external packages.

---

#### `EMAFilter` — Basic Exponential Moving Average

```python
class EMAFilter:
    def __init__(self, alpha: float, init: float = 0.0) -> None:
        self.alpha = alpha
        self.value = init

    def update(self, value: float) -> float:
        self.value = self.alpha * value + (1.0 - self.alpha) * self.value
        return self.value
```

This is the **simplest and most common** filter. It is called an **Exponential Moving Average (EMA)**.

Think of it like steering a heavy boat:
- `alpha` is how hard you can turn the wheel. A big alpha (close to 1) = fast reaction. A small alpha (close to 0) = very slow, very smooth.
- Every update it takes a little bit of the new reading and mixes it with what it remembered before.

**Formula:** `new = alpha × input + (1 − alpha) × previous`

With `alpha = 0.25` it takes about 4 updates to get halfway to a new value.

---

#### `RMSFilter` — RMS Exponential

```python
class RMSFilter:
    def __init__(self, alpha: float, init: float = 0.0) -> None:
        self.alpha = alpha
        self.value = init

    def update(self, value: float) -> float:
        self.value = sqrt(self.alpha * value**2 + (1.0 - self.alpha) * self.value**2)
        return self.value
```

Same idea as the EMA filter, but it works on **squared values** and takes a square root at the end.
This is useful when you care about the **power** of a signal (like measuring AC voltage or vibration energy) rather than its plain average.
The output is always non-negative, which makes it well suited for energy or magnitude measurements.

**Formula:** `new = sqrt(alpha × input² + (1 − alpha) × previous²)`

---

#### `AsymmetricFilter` — Different Speed Up vs. Down

```python
class AsymmetricFilter:
    def __init__(self, alpha_up: float, alpha_down: float, init: float = 0.0) -> None:
        self.alpha_up = alpha_up
        self.alpha_down = alpha_down
        self.value = init

    def update(self, value: float) -> float:
        alpha = self.alpha_up if value > self.value else self.alpha_down
        self.value = alpha * value + (1.0 - alpha) * self.value
        return self.value
```

This filter reacts **faster in one direction** than the other. You choose separate alphas for rising and falling.

Real-world example: a battery charge indicator.
You want it to show a drop quickly (so the user knows), but rise slowly (so it does not flicker back and forth).
- `alpha_up = 0.05` — rises slowly
- `alpha_down = 0.005` — falls very slowly

---

### `demo.py` — Generating Data and Plotting

```python
import pandas as pd
import matplotlib.pyplot as plt
from filters import EMAFilter, RMSFilter, AsymmetricFilter
```
We bring in our helper tools: `pandas` for the data table, `matplotlib` for drawing, and the three filter classes from `filters.py`.

---

```python
for i in range(0, TOTAL_TIME_MS, TIME_STEP_MS):
    sec = i / 1000
    num_transitions = sum(1 for t in TRANSITIONS if sec >= t)
    value = VALUE_LOW if num_transitions % 2 == 1 else VALUE_HIGH
    data["Value"].append(value)
```
This is our pretend sensor. It produces time steps every 0.1 s and switches the value between 100 and 25 at specific times — like a light switch being flipped.

```python
df = pd.DataFrame(data)
```
We put all those numbers into a pandas table (called a DataFrame) so they are easy to work with.

---

### Applying the Filters

```python
df["EMA"]        = df["Value"].apply(EMAFilter(0.25, 25.0).update)
df["RMS"]        = df["Value"].apply(RMSFilter(0.25, 25.0).update)
df["Asymmetric"] = df["Value"].apply(AsymmetricFilter(0.05, 0.005, 25.0).update)
```

We create one filter object per filter type and run every row of the data table through it one by one.
Each result is stored as a new column in the table.

---

### Plotting

```python
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
```

Finally we draw the chart with all four lines so you can compare the three filter behaviours side by side.
`plt.show()` opens a window with the plot.

---

## File Structure

```text
analog_filter/
├── filters.py       ← EMAFilter, RMSFilter, AsymmetricFilter (importable library)
├── demo.py          ← synthetic data generation and comparison plot
├── test_filters.py  ← unit tests (run with: python -m unittest test_filters -v)
├── requirements.txt
└── README.md
```
