import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


def main():
    # to-do: load the "results.csv" file from the mia-results directory

    # Get the current working directory
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, 'mia-result')

    folder_name = '2023-11-06-09-20-08'  # Change here!!!!!!!!!
    file_name = 'results.csv'

    file_path = os.path.join(target_directory, folder_name, file_name)
    print(file_path)

    # Read the data from the results.csv file
    data = pd.read_csv(file_path, sep=";")

    # to continue we need to be able to run the pipeline

    # (DONE): read the data into a list
    # (DONE) plot the Dice coefficients per label (i.e. white matter, gray matter, hippocampus, amygdala, thalamus)
    #  in a boxplot

    # Set the figure size
    plt.figure(figsize=(10, 6))

    # Use boxplot function to create boxplot for DICE
    plt.boxplot([data[data["LABEL"] == label]["DICE"]
                 for label in data["LABEL"].unique()],
                labels=data["LABEL"].unique())

    # Adding title x and y label:
    plt.title("Dice Coefficients by Label")
    plt.xlabel("Label")
    plt.ylabel("Dice Coefficients")

    # Set y-axis limits
    plt.ylim(0.4, 0.85)

    # Save the boxplot as png file
    plt.savefig("dice_boxplot.png")

    plt.show()

    # Now the same thing for the Hausdorff => uncomment this as soon as Hausdorff has been implemented and then you get
    # the boxplot

    # Set the figure size
    plt.figure(figsize=(10, 6))

    # Use boxplot function to create boxplot for HAUSDORFF
    plt.boxplot([data[data["LABEL"] == label]["HDRFDST"]
                 for label in data["LABEL"].unique()],
                labels=data["LABEL"].unique())

    # Adding title x and y label:
    plt.title("Hausdorff Coefficients by Label")
    plt.xlabel("Label")
    plt.ylabel("Hausdorff Coefficients")

    # Set y-axis limits
    plt.ylim(0, 18)

    plt.savefig("hausdorff_boxplot.png")

    plt.show()

    # labels = ["Amygdala", "GreyMatter", "Hippocampus", "Thalamus", "WhiteMatter"]

    # alternative: instead of manually loading/reading the csv file you could also use the pandas package
    # but you will need to install it first ('pip install pandas') and import it to this file ('import pandas as pd')

    # pass  # pass is just a placeholder if there is no other code


if __name__ == '__main__':
    main()