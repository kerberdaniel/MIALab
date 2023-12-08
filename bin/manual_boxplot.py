import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the brain region of interest [Amygdala, Hippocampus, Thalamus, WhiteMatter, GreyMatter]
brain_region = 'Amygdala'

# Define the type of feature to be used [GLCM, FOF, GLSZM]
feature_type = 'GLCM'

num_of_feature = 2

used_feature_name = ['Baseline', 'Mean all features']

metric = 'HDRFDST'

mean_baseline = 13.23 # NOT CHANGE
std_baseline = 1.4 # NOT CHANGE

mean_features = 13 # From excel table
std_features = 1.42 # From excel table

np.random.seed(42)
data_baseline = np.random.normal(loc=mean_baseline, scale=std_baseline, size=10000)
data_features = np.random.normal(loc=mean_features, scale=std_features, size=10000)

data= [data_baseline, data_features]




# Define folder name
folder_name = f'Specific_boxplots_{feature_type}'

# Create the folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Set font family for plots
plt.rcParams['font.family'] = 'DejaVu Serif'

# Plot boxplot for DICE scores
plt.figure(figsize=(5, 4))
positions = np.arange(1, num_of_feature * 2 + 1, 2)
positions = [1, 2]
labels = used_feature_name

# Customize boxplot appearance
plt.boxplot(data, positions=positions, labels=labels, showfliers=False, widths=0.8, patch_artist=True,
            medianprops={'color': 'black'}, boxprops={'edgecolor': 'black', 'linewidth': 2, 'facecolor': 'lightgray'})

plt.title(f'{metric} Score', fontsize=20)
# plt.xlabel('Feature name', fontsize=18)
plt.ylabel(brain_region, fontsize=18)
plt.xticks(rotation=30, ha='right', fontsize=16)

# Add text annotation in the top right corner
# text_to_display = 'Baseline: mean = 13.23, std = 1.4\nFeatures: mean = 13, std = 1.42'
# plt.text(0.95, 0.95, text_to_display, horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes, color='red', weight='medium')


# Adjust layout
plt.tight_layout()

# Activate the grid with major and minor grid lines
plt.grid(True, linestyle='-', linewidth=0.2, alpha=0.7)  # Major grid lines
plt.minorticks_on()  # Enable minor ticks
plt.grid(True, which='minor', linestyle=':', linewidth=0.2, alpha=0.5)  # Minor grid lines
# Save the figure
plt.savefig(os.path.join(folder_name, f'Boxplot_{feature_type}_{brain_region}_{metric}_man.png'), dpi=300)

plt.show()
