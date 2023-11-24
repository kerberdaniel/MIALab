import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

current_directory = os.getcwd()
parent_folder_path = os.path.join(current_directory, 'mia-result')
brain_region = 'GreyMatter'  # Change here   [Amygdala, Hippocampus, Thalamus, WhiteMatter, GreyMatter]


all_dataframes = []


for subdirectory in os.listdir(parent_folder_path):
    subdirectory_path = os.path.join(parent_folder_path, subdirectory)


    if os.path.isdir(subdirectory_path):
        csv_file_path = os.path.join(subdirectory_path, 'results_summary.csv')

        # Check if the CSV file exists
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path, delimiter='\t')
            all_dataframes.append(df)


all_data = pd.concat(all_dataframes, ignore_index=True)


all_data[['LABEL', 'METRIC', 'STATISTIC', 'VALUE']] = all_data['LABEL;METRIC;STATISTIC;VALUE'].str.split(';', expand=True)


print("Column Names:", all_data.columns)
print("First Few Rows:")
print(all_data.head())


dice_data = all_data[all_data['METRIC'] == 'DICE']
hausdorff_data = all_data[all_data['METRIC'] == 'HDRFDST']


dice_data= dice_data.iloc[:,1:5]
hausdorff_data=hausdorff_data.iloc[:,1:5]

amygdala_DICE = dice_data[dice_data['LABEL'] == brain_region]
amygdala_HDRFDST = hausdorff_data[hausdorff_data['LABEL'] == brain_region]


num_of_feature = len(amygdala_DICE) // 2


data_list_DICE = []
data_list_HDRFDST = []


for i in range(num_of_feature):
    mean_DICE, std_DICE = amygdala_DICE.iloc[i * 2: (i + 1) * 2, 3:4].values.astype(float)
    mean_HDRFDST, std_HDRFDST = amygdala_HDRFDST.iloc[i * 2: (i + 1) * 2, 3:4].values.astype(float)


    np.random.seed(42)
    data_DICE = np.random.normal(loc=mean_DICE, scale=std_DICE, size=100)
    data_list_DICE.append(data_DICE)

    data_HDRFDST = np.random.normal(loc=mean_HDRFDST, scale=std_HDRFDST, size=100)
    data_list_HDRFDST.append(data_HDRFDST)


plt.figure(figsize=(8, 5))
positions = np.arange(1, num_of_feature * 2 + 1, 2)
labels = ['Baseline'] + [f'Feature{i+1}' for i in range(1, num_of_feature)]
plt.boxplot(data_list_DICE, positions=positions, labels=labels)
plt.title('Boxplot of DICE Score')
plt.xlabel('Feature')
plt.ylabel(brain_region)

# Activate the grid with major and minor grid lines
plt.grid(True, linestyle='-', linewidth=0.2, alpha=0.7)  # Major grid lines
plt.minorticks_on()  # Enable minor ticks
plt.grid(True, which='minor', linestyle=':', linewidth=0.2, alpha=0.5)  # Minor grid lines


plt.figure(figsize=(8, 5))
positions = np.arange(1, num_of_feature * 2 + 1, 2)
labels = ['Baseline'] + [f'Feature{i+1}' for i in range(1, num_of_feature)]
plt.boxplot(data_list_HDRFDST, positions=positions, labels=labels)
plt.title('Boxplot of Hausdorff Distance')
plt.xlabel('Feature')
plt.ylabel(brain_region)

# Activate the grid with major and minor grid lines
plt.grid(True, linestyle='-', linewidth=0.2, alpha=0.7)  # Major grid lines
plt.minorticks_on()  # Enable minor ticks
plt.grid(True, which='minor', linestyle=':', linewidth=0.2, alpha=0.5)  # Minor grid lines

plt.show()