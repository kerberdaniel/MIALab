"""A medical image analysis pipeline.

The pipeline is used for brain tissue segmentation using a decision forest classifier.
"""
import argparse
import datetime
import os
import sys
import timeit
import warnings
import random

import SimpleITK as sitk
import sklearn.ensemble as sk_ensemble
import numpy as np
import pymia.data.conversion as conversion
import pymia.evaluation.writer as writer

try:
    import mialab.data.structure as structure
    import mialab.utilities.file_access_utilities as futil
    import mialab.utilities.pipeline_utilities as putil
except ImportError:
    # Append the MIALab root directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))
    import mialab.data.structure as structure
    import mialab.utilities.file_access_utilities as futil
    import mialab.utilities.pipeline_utilities as putil

LOADING_KEYS = [structure.BrainImageTypes.T1w,
                structure.BrainImageTypes.T2w,
                structure.BrainImageTypes.GroundTruth,
                structure.BrainImageTypes.BrainMask,
                structure.BrainImageTypes.RegistrationTransform]  # the list of data we will load


def main(result_dir: str, data_atlas_dir: str, data_train_dir: str, data_test_dir: str):
    """Brain tissue segmentation using decision forests.

    The main routine executes the medical image analysis pipeline:

        - Image loading
        - Registration
        - Pre-processing
        - Feature extraction
        - Decision forest classifier model building
        - Segmentation using the decision forest classifier model on unseen images
        - Post-processing of the segmentation
        - Evaluation of the segmentation
    """

    # use of random seed for better reproducibility:
    random_seed = 51
    np.random.seed(random_seed)

    # load atlas images
    putil.load_atlas_images(data_atlas_dir)

    print('-' * 5, 'Training...')

    # crawl the training image directories
    crawler = futil.FileSystemDataCrawler(data_train_dir,
                                          LOADING_KEYS,
                                          futil.BrainImageFilePathGenerator(),
                                          futil.DataDirectoryFilter())

    # set parameters for pre-processing

    glszm_parameters_list = {'SmallAreaEmphasis': False,
                             'LargeAreaEmphasis': False,
                             'GrayLevelNonUniformity': False,
                             'GrayLevelNonUniformityNormalized': False,
                             'SizeZoneNonUniformity': False,
                             'SizeZoneNonUniformityNormalized': False,
                             'ZonePercentage': False,
                             'GrayLevelVariance': False,
                             'ZoneVariance': False,
                             'ZoneEntropy': False,
                             'LowGrayLevelZoneEmphasis': False,
                             'HighGrayLevelZoneEmphasis': False,
                             'SmallAreaLowGrayLevelEmphasis': False,
                             'SmallAreaHighGrayLevelEmphasis': False,
                             'LargeAreaLowGrayLevelEmphasis': False,
                             'LargeAreaHighGrayLevelEmphasis': False,
                             }

    fo_parameters_list = {'10Percentile': False,
                          '90Percentile': False,
                          'Energy': False,
                          'Entropy': False,
                          'InterquartileRange': False,
                          'Kurtosis': False,
                          'Maximum': False,
                          'MeanAbsoluteDeviation': False,
                          'Mean': False,
                          'Median': False,
                          'Minimum': False,
                          'Range': False,
                          'RobustMeanAbsoluteDeviation': False,
                          'RootMeanSquared': False,
                          'Skewness': False,
                          'TotalEnergy': False,
                          'Uniformity': False,
                          'Variance': False}

    glcm_parameters_list = {'Autocorrelation': True,
                            'ClusterProminence': False,
                            'ClusterShade': False,
                            'ClusterTendency': False,
                            'Contrast': False,
                            'Correlation': False,
                            'DifferenceAverage': False,
                            'DifferenceEntropy': False,
                            'DifferenceVariance': False,
                            'Id': False,
                            'Idm': False,
                            'Idmn': False,
                            'Idn': False,
                            'Imc1': False,
                            'Imc2': False,
                            'InverseVariance': False,
                            'JointAverage': False,  # cause error
                            'JointEnergy': False,
                            'JointEntropy': False,
                            'MCC': False,  # cause error
                            'MaximumProbability': False,
                            'SumAverage': False,  # cause error
                            'SumEntropy': False,
                            'SumSquares': False}

    pre_process_params = {'skullstrip_pre': True,
                          'normalization_pre': True,
                          'registration_pre': True,
                          'coordinates_feature': True,
                          'intensity_feature': True,
                          'gradient_intensity_feature': True,
                          'GLCM_features': True,  # Enable GLCM feature extraction
                          'GLCM_features_parameters': glcm_parameters_list,
                          'FO_features': False,  # Enable FO feature extraction
                          'FO_features_parameters': fo_parameters_list,
                          'GLSZM_features': False,  # Enable GLSZM feature extraction
                          'GLSZM_features_parameters': glszm_parameters_list,
                          'n_estimators': 50,
                          'max_depth': 60
                          }

    # 'GLCM_features_parameters': glcm_parameters_list,
    # load images for training and pre-process
    images = putil.pre_process_batch(crawler.data, pre_process_params, multi_process=False)

    # generate feature matrix and label vector
    data_train = np.concatenate([img.feature_matrix[0] for img in images])
    labels_train = np.concatenate([img.feature_matrix[1] for img in images]).squeeze()

    # warnings.warn('Random forest parameters not properly set.')
    # forest = sk_ensemble.RandomForestClassifier(max_features=images[0].feature_matrix[0].shape[1],
    #                                             n_estimators=1,
    #                                             max_depth=5)

    forest = sk_ensemble.RandomForestClassifier(max_features=images[0].feature_matrix[0].shape[1],
                                                n_estimators=pre_process_params['n_estimators'],
                                                max_depth=pre_process_params['max_depth'])

    start_time = timeit.default_timer()
    forest.fit(data_train, labels_train)
    print(' Time elapsed:', timeit.default_timer() - start_time, 's')

    # create a result directory with timestamp
    t = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    result_dir = os.path.join(result_dir, t)
    os.makedirs(result_dir, exist_ok=True)

    # Save parameters to a text file in the timestamped result directory
    params_file_path = os.path.join(result_dir, 'parameters.txt')

    def write_params_to_file(params, file, depth=0):
        for key, value in params.items():
            if value is True:
                file.write(f'{"  " * depth}{key}: {value}\n')
            elif isinstance(value, dict):
                file.write(f'{"  " * depth}{key}:\n')
                if not any(value.values()):  # Check if any value in the nested dictionary is True
                    file.write(f'{"  " * (depth + 1)}NO feature active\n')
                else:
                    write_params_to_file(value, file, depth + 1)

    with open(params_file_path, 'w') as params_file:
        write_params_to_file(pre_process_params, params_file)

    print('-' * 5, 'Testing...')

    # initialize evaluator
    evaluator = putil.init_evaluator()

    # crawl the training image directories
    crawler = futil.FileSystemDataCrawler(data_test_dir,
                                          LOADING_KEYS,
                                          futil.BrainImageFilePathGenerator(),
                                          futil.DataDirectoryFilter())

    # load images for testing and pre-process
    pre_process_params['training'] = False
    images_test = putil.pre_process_batch(crawler.data, pre_process_params, multi_process=False)

    images_prediction = []
    images_probabilities = []

    for img in images_test:
        print('-' * 10, 'Testing', img.id_)

        start_time = timeit.default_timer()
        predictions = forest.predict(img.feature_matrix[0])
        probabilities = forest.predict_proba(img.feature_matrix[0])
        print(' Time elapsed:', timeit.default_timer() - start_time, 's')

        # convert prediction and probabilities back to SimpleITK images
        image_prediction = conversion.NumpySimpleITKImageBridge.convert(predictions.astype(np.uint8),
                                                                        img.image_properties)
        image_probabilities = conversion.NumpySimpleITKImageBridge.convert(probabilities, img.image_properties)

        # evaluate segmentation without post-processing
        evaluator.evaluate(image_prediction, img.images[structure.BrainImageTypes.GroundTruth], img.id_)

        images_prediction.append(image_prediction)
        images_probabilities.append(image_probabilities)

    # post-process segmentation and evaluate with post-processing
    post_process_params = {'simple_post': True}
    images_post_processed = putil.post_process_batch(images_test, images_prediction, images_probabilities,
                                                     post_process_params, multi_process=True)

    for i, img in enumerate(images_test):
        evaluator.evaluate(images_post_processed[i], img.images[structure.BrainImageTypes.GroundTruth],
                           img.id_ + '-PP')

        # save results
        sitk.WriteImage(images_prediction[i], os.path.join(result_dir, images_test[i].id_ + '_SEG.mha'), True)
        sitk.WriteImage(images_post_processed[i], os.path.join(result_dir, images_test[i].id_ + '_SEG-PP.mha'), True)

    # use two writers to report the results
    os.makedirs(result_dir, exist_ok=True)  # generate result directory, if it does not exists
    result_file = os.path.join(result_dir, 'results.csv')
    writer.CSVWriter(result_file).write(evaluator.results)

    print('\nSubject-wise results...')
    writer.ConsoleWriter().write(evaluator.results)

    # report also mean and standard deviation among all subjects
    result_summary_file = os.path.join(result_dir, 'results_summary.csv')
    functions = {'MEAN': np.mean, 'STD': np.std}
    writer.CSVStatisticsWriter(result_summary_file, functions=functions).write(evaluator.results)
    print('\nAggregated statistic results...')
    writer.ConsoleStatisticsWriter(functions=functions).write(evaluator.results)

    # clear results such that the evaluator is ready for the next evaluation
    evaluator.clear()


if __name__ == "__main__":
    """The program's entry point."""

    script_dir = os.path.dirname(sys.argv[0])

    parser = argparse.ArgumentParser(description='Medical image analysis pipeline for brain tissue segmentation')

    parser.add_argument(
        '--result_dir',
        type=str,
        default=os.path.normpath(os.path.join(script_dir, './mia-result')),
        help='Directory for results.'
    )

    parser.add_argument(
        '--data_atlas_dir',
        type=str,
        default=os.path.normpath(os.path.join(script_dir, '../data/atlas')),
        help='Directory with atlas data.'
    )

    parser.add_argument(
        '--data_train_dir',
        type=str,
        default=os.path.normpath(os.path.join(script_dir, '../data/train/')),
        help='Directory with training data.'
    )

    parser.add_argument(
        '--data_test_dir',
        type=str,
        default=os.path.normpath(os.path.join(script_dir, '../data/test/')),
        help='Directory with testing data.'
    )

    args = parser.parse_args()
    main(args.result_dir, args.data_atlas_dir, args.data_train_dir, args.data_test_dir)
