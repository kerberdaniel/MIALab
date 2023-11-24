import os
import datetime

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
# create a result directory with timestamp
result_dir = os.getcwd()
t = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
result_dir = os.path.join(result_dir, t)
os.makedirs(result_dir, exist_ok=True)
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