import numpy as np
import matplotlib.pyplot as plt
T_max = 38
T_min = 2
T_opt = 24
alpha = np.log(2) / np.log((T_max - T_min) / (T_opt - T_min))
print(alpha)

beta = np.linspace(0, 1, 100)  # beta ranging from 0 to 1

# Define the function f(T)
def f(T, T_min, T_opt, alpha, beta):
    return (2 * (T - T_min) ** alpha * (T_opt - T_min) ** alpha - (T - T_min) ** (2 * alpha)) / ((T_opt - T_min) ** (2 * alpha))

# Create a range of temperature values
T_values = np.linspace(T_min, T_max, 100)

# Calculate the function values for different beta
f_values = np.array([f(T_values, T_min, T_opt, alpha, b) for b in beta])

# Plotting
plt.figure(figsize=(10, 6))
for i, b in enumerate(beta):
    plt.plot(T_values, f_values[i], label=f'b = {b:.2f}', alpha=0.5)
plt.show()