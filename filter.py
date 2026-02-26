import pandas as pd
import matplotlib.pyplot as plt
from math import sqrt

# Example Data
data = {"Time": [], "Value": []}

for i in range(0, 4000, 100):
    sec = i/1000
    data["Time"].append(sec)
    if sec < 4:
        if sec < 2:
            data["Value"].append(100.0)
        else:
            data["Value"].append(25.0)
    elif sec < 10:
        data["Value"].append(100.0)    
    elif sec < 15:
        data["Value"].append(25.0)    
    else:
        data["Value"].append(100.0)
        
df = pd.DataFrame(data)
    
class filter:
    def __init__(self, alpha, init):
        self.alpha = alpha
        self.value = init

    def update(self, value):
        self.value = self.alpha * value + (1 - self.alpha) * self.value
        return self.value	

class filter1:
    def __init__(self, alpha):
        self.alpha = alpha
        self.value = 0.0

    def update(self, value):
        self.value = sqrt(self.alpha * (value * value ) + (1 - self.alpha) * (self.value * self.value))
        return self.value	

class filter2:
    def __init__(self, alpha_up, alpha_down):
        self.alpha_up = alpha_up
        self.alpha_down = alpha_down
        self.value = 0.0

    def update(self, value):
        alpha = self.alpha_up if value > self.value else self.alpha_down
        self.value = alpha * value + (1 - alpha) * self.value
        return self.value
    
# Plot
alpha = 0.25
alpha_up = 0.05
alpha_down = 0.005
f = filter(alpha, 25.0)
f1 = filter1(alpha)
f2 = filter2(alpha_up, alpha_down)

f3 = filter2(1/16, 1/256)
# Apply filter to the data
df["Value_Filtered"]  = df["Value"].apply(f.update)
# df["Value_Filtered1"] = df["Value"].apply(f1.update)
# df["Value_Filtered2"] = df["Value"].apply(f2.update)
# df["Value_Filtered3"] = df["Value"].apply(f3.update)

print(df.head())


# add the filtered and input data to the plot
plt.figure()
plt.plot(df["Time"], df["Value"], label="Input Data")
plt.plot(df["Time"], df["Value_Filtered"], label="Filtered Data")
# plt.plot(df["Time"], df["Value_Filtered1"], label="Filtered Data1")
# plt.plot(df["Time"], df["Value_Filtered2"], label="Filtered Data2")
# plt.plot(df["Time"], df["Value_Filtered3"], label="Filtered Data3")
plt.xlabel("Time")
plt.ylabel("Value")
plt.legend()

plt.show()

