import os
import pandas as pd

# Define the type of feature to be used [GLCM, FOF, GLSZM]
feature_type = 'FOF'


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


# Define the parent folder path
current_directory = os.getcwd()
parent_folder_path = os.path.join(current_directory, f'mia-result/{feature_type}')

# Loop through brain regions
for brain_region in ['Amygdala', 'Hippocampus', 'Thalamus', 'WhiteMatter', 'GreyMatter']:
    all_dataframes = []

    # Loop through folders in the specified order
    for subdirectory in get_used_features():
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

    mean_DICE_list = []
    std_DICE_list = []
    mean_HDRFDST_list = []
    std_HDRFDST_list = []

    # Generate random data for DICE and Hausdorff distance based on mean and standard deviation
    for i in range(num_of_feature):
        mean_DICE, std_DICE = structure_DICE.iloc[i * 2: (i + 1) * 2, 3:4].values.astype(float)
        mean_HDRFDST, std_HDRFDST = structure_HDRFDST.iloc[i * 2: (i + 1) * 2, 3:4].values.astype(float)
        # Append values to lists
        mean_DICE_list.append(mean_DICE)
        std_DICE_list.append(std_DICE)
        mean_HDRFDST_list.append(mean_HDRFDST)
        std_HDRFDST_list.append(std_HDRFDST)

    # Create a DataFrame
    dataframe_dice = {
        f'Feature_{feature_type}': get_used_features(),
        'Mean_DICE': mean_DICE_list,
        'Std_DICE': std_DICE_list
    }
    df_DICE = pd.DataFrame(dataframe_dice)

    # Convert lists to strings and remove square brackets
    df_DICE['Mean_DICE'] = df_DICE['Mean_DICE'].astype(str).str.strip('[]')
    df_DICE['Std_DICE'] = df_DICE['Std_DICE'].astype(str).str.strip('[]')

    # Create a DataFrame for HDRFDST
    dataframe_hdrfdst = {
        'Mean_HDRFDST': mean_HDRFDST_list,
        'Std_HDRFDST': std_HDRFDST_list
    }
    df_HDRFDST = pd.DataFrame(dataframe_hdrfdst)

    # Convert lists to strings and remove square brackets
    df_HDRFDST['Mean_HDRFDST'] = df_HDRFDST['Mean_HDRFDST'].astype(str).str.strip('[]')
    df_HDRFDST['Std_HDRFDST'] = df_HDRFDST['Std_HDRFDST'].astype(str).str.strip('[]')

    combined_df_horizontal = pd.concat([df_DICE, df_HDRFDST], axis=1)

    # Create the folder if it doesn't exist
    folder_name = f'summary_table'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Save the DataFrame to an Excel file
    excel_file_path = os.path.join(folder_name, f'summary_{brain_region}_{feature_type}.xlsx')
    combined_df_horizontal.to_excel(excel_file_path, index=False)

    print(f"DataFrame for {brain_region} saved to '{excel_file_path}'.")
