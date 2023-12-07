import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


def main():

    # Get the current working directory
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, 'mia-result')

    folder_name_baseline = 'a_baseline'  # Change here!!!!!!!!!# Baseline
    folder_name_features = 'Baseline_2'  # Change here!!!!!!!!!
    file_name = 'results.csv'

    file_path_baseline = os.path.join(target_directory, folder_name_baseline, file_name)
    print(file_path_baseline)

    file_path_features = os.path.join(target_directory, folder_name_features, file_name)
    print(file_path_features)

    # Read the data from the results.csv file
    baseline = pd.read_csv(file_path_baseline, sep=";")
    features = pd.read_csv(file_path_features, sep=";")

    ############ DICE PLOTTING
    # Create a list of labels
    labels = baseline["LABEL"].unique()

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Define a color for the baseline and features boxplots
    baseline_color = 'blue'
    features_color = 'green'

    # Initialize a position variable
    position = 1

    # Create lists to store data for baseline and features
    baseline_data = []
    features_data = []

    # Adjust the positions for labels and boxplots
    label_positions = range(1, len(labels) * 3, 3)
    baseline_positions = [pos - 0.25 for pos in label_positions]
    features_positions = [pos + 0.25 for pos in label_positions]

    # Iterate over labels and extract DICE values for baseline and features
    for label in labels:
        baseline_data.append(baseline[baseline["LABEL"] == label]["DICE"])
        features_data.append(features[features["LABEL"] == label]["DICE"])

    # Create boxplots for baseline data
    boxplot1 = ax.boxplot(baseline_data, positions=baseline_positions, widths=0.4, patch_artist=True)
    for box in boxplot1['boxes']:
        box.set(facecolor=baseline_color)

    # Create boxplots for features data
    boxplot2 = ax.boxplot(features_data, positions=features_positions, widths=0.4, patch_artist=True)
    for box in boxplot2['boxes']:
        box.set(facecolor=features_color)

    # Set y-axis limits
    ax.set_ylim(0.4, 0.85)

    # Add x-axis labels for each label
    ax.set_xticks(label_positions)
    ax.set_xticklabels(labels)

    # Adding title and labels
    plt.title("Dice Coefficients by Label")
    plt.xlabel("Label")
    plt.ylabel("Dice Coefficients")

    # Create a legend
    legend_labels = ['Baseline', 'Features']
    handles = [plt.Rectangle((0, 0), 1, 1, color=baseline_color), plt.Rectangle((0, 0), 1, 1, color=features_color)]
    ax.legend(handles, legend_labels)

    # Save the boxplot as a PNG file
    plt.savefig("dice_boxplot.png")

    plt.show()


    ############ HAUSDORFF PLOTTING
    # Create a list of labels
    labels = baseline["LABEL"].unique()

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    # Define a color for the baseline and features boxplots
    baseline_color = 'blue'
    features_color = 'green'

    # Initialize a position variable
    position = 1

    # Create lists to store data for baseline and features
    baseline_data = []
    features_data = []

    # Adjust the positions for labels and boxplots
    label_positions = range(1, len(labels) * 3, 3)
    baseline_positions = [pos - 0.25 for pos in label_positions]
    features_positions = [pos + 0.25 for pos in label_positions]

    # Iterate over labels and extract DICE values for baseline and features
    for label in labels:
        baseline_data.append(baseline[baseline["LABEL"] == label]["HDRFDST"])
        features_data.append(features[features["LABEL"] == label]["HDRFDST"])

    # Create boxplots for baseline data
    boxplot1 = ax.boxplot(baseline_data, positions=baseline_positions, widths=0.4, patch_artist=True)
    for box in boxplot1['boxes']:
        box.set(facecolor=baseline_color)

    # Create boxplots for features data
    boxplot2 = ax.boxplot(features_data, positions=features_positions, widths=0.4, patch_artist=True)
    for box in boxplot2['boxes']:
        box.set(facecolor=features_color)

    # Set y-axis limits
    ax.set_ylim(1, 17.5)

    # Add x-axis labels for each label
    ax.set_xticks(label_positions)
    ax.set_xticklabels(labels)

    # Adding title and labels
    plt.title("Hausdorff Distance by Label")
    plt.xlabel("Label")
    plt.ylabel("Hausdorff Coefficients")

    # Create a legend
    legend_labels = ['Baseline', 'Features']
    handles = [plt.Rectangle((0, 0), 1, 1, color=baseline_color), plt.Rectangle((0, 0), 1, 1, color=features_color)]
    ax.legend(handles, legend_labels)

    # Save the boxplot as a PNG file
    plt.savefig("hausdorff_boxplot.png")

    plt.show()

    # labels = ["Amygdala", "GreyMatter", "Hippocampus", "Thalamus", "WhiteMatter"]

    # alternative: instead of manually loading/reading the csv file you could also use the pandas package
    # but you will need to install it first ('pip install pandas') and import it to this file ('import pandas as pd')

    # pass  # pass is just a placeholder if there is no other code


if __name__ == '__main__':
    main()