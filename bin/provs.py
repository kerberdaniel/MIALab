import numpy as np
import matplotlib.pyplot as plt

# Set mean and std for the distribution
desired_mean = 10
std = 2

# Generate synthetic data based on normal distribution
data = np.random.normal(0, std, 100)  # Generate data with mean=0
data_shifted = data + (desired_mean - np.mean(data))  # Shift the data to match the desired mean

# Create a boxplot using Matplotlib
plt.boxplot(data_shifted, vert=False)
plt.title('Boxplot with Mean and Std')
plt.xlabel('Values')
plt.show()
