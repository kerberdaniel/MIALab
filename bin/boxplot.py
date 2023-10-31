import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


def main():
    # to-do: load the "results.csv" file from the mia-results directory

    # Get the current working directory
    current_directory = os.getcwd()
    target_directory = os.path.join(current_directory, 'mia-result')

    folder_name = '2023-10-31-14-59-59' # change here
    file_name = 'results.csv'

    file_path = os.path.join(target_directory, folder_name, file_name)
    print(file_path)

    data = pd.read_csv(filepath)

    # to continue we need to be able to run the pipeline

    # todo: read the data into a list
    # todo: plot the Dice coefficients per label (i.e. white matter, gray matter, hippocampus, amygdala, thalamus)
    #  in a boxplot

    # alternative: instead of manually loading/reading the csv file you could also use the pandas package
    # but you will need to install it first ('pip install pandas') and import it to this file ('import pandas as pd')


    # pass  # pass is just a placeholder if there is no other code


if __name__ == '__main__':
    main()
