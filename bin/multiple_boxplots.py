import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Define the brain region of interest [Amygdala, Hippocampus, Thalamus, WhiteMatter, GreyMatter]
brain_region = 'GreyMatter'

# Define the type of feature to be used [GLCM, FOF, GLSZM]
feature_type = 'GLSZM'


def get_used_features():
    # Define the features based on the chosen type [GLCM, FOF, GLSZM]
    if feature_type == 'GLCM':
        parameters = ['Baseline', 'Autocorrelation', 'ClusterProminence', 'ClusterShade', 'ClusterTendency',
                      'Contrast', 'Correlation', 'DifferenceAverage', 'DifferenceEntropy', 'DifferenceVariance',
                      'Id', 'Idm', 'Idmn', 'Idn', 'Imc1', 'Imc2', 'InverseVariance', 'JointEnergy', 'JointEntropy',
                      'MaximumProbability', 'SumEntropy', 'SumSquares']
    elif feature_type == 'FOF':
        parameters = ['Baseline', '10Percentile', '90Percentile', 'Energy', 'Entropy', 'InterquartileRange',
                      'Kurtosis', 'Maximum', 'MeanAbsoluteDeviation', 'Mean', 'Median', 'Minimum', 'Range',
                      'RootMeanSquared', 'Skewness', 'TotalEnergy', 'Uniformity', 'Variance']
    elif feature_type == 'GLSZM':
        parameters = ['Baseline', 'GrayLevelNonUniformity', 'GrayLevelNonUniformityNormalized', 'GrayLevelVariance',
                      'HighGrayLevelZoneEmphasis', 'LargeAreaEmphasis', 'LargeAreaHighGrayLevelEmphasis',
                      'LargeAreaLowGrayLevelEmphasis', 'LowGrayLevelZoneEmphasis', 'SizeZoneNonUniformity',
                      'SizeZoneNonUniformityNormalized', 'SmallAreaEmphasis', 'SmallAreaHighGrayLevelEmphasis',
                      'SmallAreaLowGrayLevelEmphasis',
                      'ZoneEntropy', 'ZonePercentage', 'ZoneVariance']
    else:
        raise ValueError("Invalid feature type. Choose from: [GLCM, FOF, GLSZM]")

    return parameters


current_directory = os.getcwd()
parent_folder_path = os.path.join(current_directory, f'mia-result/{feature_type}')
all_dataframes = []

# Loop through subdirectories in the parent folder
for subdirectory in os.listdir(parent_folder_path):
    subdirectory_path = os.path.join(parent_folder_path, subdirectory)

    if os.path.isdir(subdirectory_path):
        csv_file_path = os.path.join(subdirectory_path, 'results_summary.csv')

        # Check if the CSV file exists
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path, delimiter='\t')
            all_dataframes.append(df)

# Combine all dataframes into a single dataframe
all_data = pd.concat(all_dataframes, ignore_index=True)

# Split the combined column 'LABEL;METRIC;STATISTIC;VALUE' into separate columns
all_data[['LABEL', 'METRIC', 'STATISTIC', 'VALUE']] = all_data['LABEL;METRIC;STATISTIC;VALUE'].str.split(';',
                                                                                                         expand=True)

# Display column names and a few rows of the combined dataframe
print("Column Names:", all_data.columns)
print("First Few Rows:")
print(all_data.head())

# Extract DICE and Hausdorff distance data
dice_data = all_data[all_data['METRIC'] == 'DICE']
hausdorff_data = all_data[all_data['METRIC'] == 'HDRFDST']

# Select relevant columns for analysis
dice_data = dice_data.iloc[:, 1:5]
hausdorff_data = hausdorff_data.iloc[:, 1:5]

# Extract data for the specified brain region
structure_DICE = dice_data[dice_data['LABEL'] == brain_region]
structure_HDRFDST = hausdorff_data[hausdorff_data['LABEL'] == brain_region]

# Calculate the number of features
num_of_feature = len(structure_DICE) // 2

data_list_DICE = []
data_list_HDRFDST = []
mean_dice_baseline = 0
mean_hdrfdst_baseline = 0

# Generate random data for DICE and Hausdorff distance based on mean and standard deviation
for i in range(num_of_feature):
    mean_DICE, std_DICE = structure_DICE.iloc[i * 2: (i + 1) * 2, 3:4].values.astype(float)
    mean_HDRFDST, std_HDRFDST = structure_HDRFDST.iloc[i * 2: (i + 1) * 2, 3:4].values.astype(float)

    if i == 0:
        mean_dice_baseline = mean_DICE
        mean_hdrfdst_baseline = mean_HDRFDST

    np.random.seed(42)
    data_DICE = np.random.normal(loc=mean_DICE, scale=std_DICE, size=10000)
    data_list_DICE.append(data_DICE)

    data_HDRFDST = np.random.normal(loc=mean_HDRFDST, scale=std_HDRFDST, size=10000)
    data_list_HDRFDST.append(data_HDRFDST)

# Define folder name
folder_name = f'Boxplots_{feature_type}'

# Create the folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Set font family for plots
plt.rcParams['font.family'] = 'DejaVu Serif'

# Plot boxplot for DICE scores
plt.figure(figsize=(16, 8))
positions = np.arange(1, num_of_feature * 2 + 1, 2)
labels = get_used_features()

# Customize boxplot appearance
plt.boxplot(data_list_DICE, positions=positions, labels=labels, showfliers=False, widths=0.8, patch_artist=True,
            medianprops={'color': 'black'}, boxprops={'edgecolor': 'black', 'linewidth': 2, 'facecolor': 'lightgray'})

plt.title('DICE Score', fontsize=20)
plt.xlabel('Feature name', fontsize=18)
plt.ylabel(brain_region, fontsize=18)
plt.xticks(rotation=30, ha='right', fontsize=16)

# Add a line on the y-axis for the mean value of the first boxplot
plt.axhline(y=mean_dice_baseline, color='red', linestyle='--', linewidth=1.5, label='Baseline mean Value')

# Show legend
plt.legend(fontsize='large', loc='upper right')
# Adjust layout
plt.tight_layout()

# Activate the grid with major and minor grid lines
plt.grid(True, linestyle='-', linewidth=0.2, alpha=0.7)  # Major grid lines
plt.minorticks_on()  # Enable minor ticks
plt.grid(True, which='minor', linestyle=':', linewidth=0.2, alpha=0.5)  # Minor grid lines
# Save the figure
plt.savefig(os.path.join(folder_name, f'Boxplot_{feature_type}_{brain_region}_DICE.png'), dpi=300)

# Plot boxplot for Hausdorff distance
plt.figure(figsize=(16, 8))
positions = np.arange(1, num_of_feature * 2 + 1, 2)
labels = get_used_features()

# Customize boxplot appearance
plt.boxplot(data_list_HDRFDST, positions=positions, showfliers=False, labels=labels, widths=0.8, patch_artist=True,
            medianprops={'color': 'black'}, boxprops={'edgecolor': 'black', 'linewidth': 2, 'facecolor': 'lightgray'})

plt.title('Hausdorff Distance', fontsize=20)
plt.xlabel(f'{feature_type} feature', fontsize=18)
plt.ylabel(brain_region, fontsize=16)

plt.xticks(rotation=30, ha='right', fontsize=16)

# Add a line on the y-axis for the mean value of the first boxplot
plt.axhline(y=mean_hdrfdst_baseline, color='red', linestyle='--', linewidth=1.5, label='Baseline mean Value')

# Show legend
plt.legend(fontsize='large', loc='upper right')

# Adjust layout
plt.tight_layout()

# Activate the grid with major and minor grid lines
plt.grid(True, linestyle='-', linewidth=0.2, alpha=0.7)  # Major grid lines
plt.minorticks_on()  # Enable minor ticks
plt.grid(True, which='minor', linestyle=':', linewidth=0.2, alpha=0.5)  # Minor grid lines
# Save the figure
plt.savefig(os.path.join(folder_name, f'Boxplot_{feature_type}_{brain_region}_HDRFDST.png'), dpi=300)
plt.show()
