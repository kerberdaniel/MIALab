"""This module contains utility classes and functions."""
import enum
import os
import typing as t

import SimpleITK as sitk
import numpy as np
import pymia.data.conversion as conversion
import pymia.evaluation.evaluator as eval_
import pymia.evaluation.metric as metric
import pymia.filtering.filter as fltr
from radiomics import featureextractor, glcm, firstorder, glszm

import mialab.data.structure as structure
import mialab.filtering.feature_extraction as fltr_feat
import mialab.filtering.postprocessing as fltr_postp
import mialab.filtering.preprocessing as fltr_prep
import mialab.utilities.multi_processor as mproc

atlas_t1 = sitk.Image()
atlas_t2 = sitk.Image()


def load_atlas_images(directory: str):
    """Loads the T1 and T2 atlas images.

    Args:
        directory (str): The atlas data directory.
    """

    global atlas_t1
    global atlas_t2
    atlas_t1 = sitk.ReadImage(os.path.join(directory, 'mni_icbm152_t1_tal_nlin_sym_09a_mask.nii.gz'))
    atlas_t2 = sitk.ReadImage(os.path.join(directory, 'mni_icbm152_t2_tal_nlin_sym_09a.nii.gz'))
    if not conversion.ImageProperties(atlas_t1) == conversion.ImageProperties(atlas_t2):
        raise ValueError('T1w and T2w atlas images have not the same image properties')


class FeatureImageTypes(enum.Enum):
    """Represents the feature image types."""

    ATLAS_COORD = 1

    T1w_INTENSITY = 2
    T1w_GRADIENT_INTENSITY = 3

    T2w_INTENSITY = 4
    T2w_GRADIENT_INTENSITY = 5

    T1w_GLCM = 6  # GLCM feature for T1-weighted images
    T2w_GLCM = 7  # GLCM feature for T2-weighted images

    T1w_FO = 8  # FO feature for T1-weighted images
    T2w_FO = 9  # FO feature for T2-weighted images

    T1w_GLSZM = 10  # GLSZM feature for T1-weighted images
    T2w_GLSZM = 11  # GLSZM feature for T1-weighted images


class FeatureExtractor:
    """Represents a feature extractor."""

    def __init__(self, img: structure.BrainImage, **kwargs):
        """Initializes a new instance of the FeatureExtractor class.

        Args:
            img (structure.BrainImage): The image to extract features from.
        """
        self.img = img
        self.training = kwargs.get('training', True)
        self.coordinates_feature = kwargs.get('coordinates_feature', False)
        self.intensity_feature = kwargs.get('intensity_feature', False)
        self.gradient_intensity_feature = kwargs.get('gradient_intensity_feature', False)

        # get feature type
        self.GLCM_features = kwargs.get('GLCM_features', False)
        self.FO_features = kwargs.get('FO_features', False)
        self.GLSZM_features = kwargs.get('GLSZM_features', False)

        # get the feature extraction parameters
        self.GLCM_features_parameters = kwargs.get('GLCM_features_parameters', {})
        self.FO_features_parameters = kwargs.get('FO_features_parameters', {})
        self.GLSZM_features_parameters = kwargs.get('GLSZM_features_parameters', {})


        # Initialize PyRadiomics feature extractor for GLCM features
        if self.GLCM_features:
            self.pyradiomics_extractor_GLCM = featureextractor.RadiomicsFeatureExtractor()
            self.pyradiomics_extractor_GLCM.disableAllFeatures()
            self.pyradiomics_extractor_GLCM.enableFeatureClassByName('glcm')

        # Initialize PyRadiomics feature extractor for FO features
        if self.FO_features:
            self.pyradiomics_extractor_FO = featureextractor.RadiomicsFeatureExtractor()
            self.pyradiomics_extractor_FO.disableAllFeatures()
            self.pyradiomics_extractor_FO.enableFeatureClassByName('firstorder')

        # Initialize PyRadiomics feature extractor for GLSZM features
        if self.GLSZM_features:
            self.pyradiomics_extractor_GLSZM = featureextractor.RadiomicsFeatureExtractor()
            self.pyradiomics_extractor_GLSZM.disableAllFeatures()
            self.pyradiomics_extractor_GLSZM.enableFeatureClassByName('glszm')

    @property
    def execute(self) -> structure.BrainImage:
        """Extracts features from an image.

        Returns:
            structure.BrainImage: The image with extracted features.
        """
        # warnings.warn('No features from T2-weighted image extracted.')

        if self.coordinates_feature:
            atlas_coordinates = fltr_feat.AtlasCoordinates()
            self.img.feature_images[FeatureImageTypes.ATLAS_COORD] = \
                atlas_coordinates.execute(self.img.images[structure.BrainImageTypes.T1w])

        if self.intensity_feature:
            self.img.feature_images[FeatureImageTypes.T1w_INTENSITY] = self.img.images[structure.BrainImageTypes.T1w]
            self.img.feature_images[FeatureImageTypes.T2w_INTENSITY] = self.img.images[structure.BrainImageTypes.T2w]

        if self.gradient_intensity_feature:
            # compute gradient magnitude images
            self.img.feature_images[FeatureImageTypes.T1w_GRADIENT_INTENSITY] = \
                sitk.GradientMagnitude(self.img.images[structure.BrainImageTypes.T1w])
            self.img.feature_images[FeatureImageTypes.T2w_GRADIENT_INTENSITY] = \
                sitk.GradientMagnitude(self.img.images[structure.BrainImageTypes.T2w])

        # compute GLCM features
        if self.GLCM_features:

            # Enable GLCM features based on the specified GLCM feature parameters
            glcmT1w_features = glcm.RadiomicsGLCM(self.img.images[structure.BrainImageTypes.T1w],
                                                  self.img.images[structure.BrainImageTypes.BrainMask],
                                                  voxelBased=True)

            # Print the GLCM features that are in use
            print("GLCM features in use:", [key for key, value in self.GLCM_features_parameters.items() if value])

            # Enable specified GLCM features
            glcmT1w_features.enabledFeatures = self.GLCM_features_parameters

            # Execute GLCM feature extraction on the T1-weighted image
            self.img.feature_images[FeatureImageTypes.T1w_GLCM] = glcmT1w_features.execute()

            # Combine individual GLCM features into a composite image (if needed)
            composite_image_t1 = sitk.Compose(list(self.img.feature_images[FeatureImageTypes.T1w_GLCM].values()))

            # Copy information from the original T1-weighted image
            composite_image_t1.CopyInformation(self.img.images[structure.BrainImageTypes.T1w])

            # Store the composite image
            self.img.feature_images[FeatureImageTypes.T1w_GLCM] = composite_image_t1

            # Enable GLCM features based on the specified GLCM feature parameters for T2-weighted image
            glcmT2w_features = glcm.RadiomicsGLCM(self.img.images[structure.BrainImageTypes.T2w],
                                                  self.img.images[structure.BrainImageTypes.BrainMask],
                                                  voxelBased=True)

            # Enable specified GLCM features for T2-weighted image
            glcmT2w_features.enabledFeatures = self.GLCM_features_parameters

            # Execute GLCM feature extraction on the T2-weighted image
            self.img.feature_images[FeatureImageTypes.T2w_GLCM] = glcmT2w_features.execute()

            # Combine individual GLCM features into a composite image for T2-weighted (if needed)
            composite_image_t2 = sitk.Compose(list(self.img.feature_images[FeatureImageTypes.T2w_GLCM].values()))

            # Copy information from the original T2-weighted image
            composite_image_t2.CopyInformation(self.img.images[structure.BrainImageTypes.T2w])

            # Store the composite image for T2-weighted
            self.img.feature_images[FeatureImageTypes.T2w_GLCM] = composite_image_t2

        # compute FO features
        if self.FO_features:

            # Enable FO features based on the specified FO feature parameters
            foT1w_features = firstorder.RadiomicsFirstOrder(self.img.images[structure.BrainImageTypes.T1w],
                                                            self.img.images[structure.BrainImageTypes.BrainMask],
                                                            voxelBased=True)

            # Print the FO features that are in use
            print("FO features in use:", [key for key, value in self.FO_features_parameters.items() if value])

            # Enable specified FO features
            foT1w_features.enabledFeatures = self.FO_features_parameters

            # Execute FO feature extraction on the T1-weighted image
            self.img.feature_images[FeatureImageTypes.T1w_FO] = foT1w_features.execute()

            # Combine individual FO features into a composite image (if needed)
            composite_image_t1_fo = sitk.Compose(list(self.img.feature_images[FeatureImageTypes.T1w_FO].values()))

            # Copy information from the original T1-weighted image
            composite_image_t1_fo.CopyInformation(self.img.images[structure.BrainImageTypes.T1w])

            # Store the composite image for T1-weighted FO
            self.img.feature_images[FeatureImageTypes.T1w_FO] = composite_image_t1_fo

            # Enable FO features based on the specified FO feature parameters for T2-weighted image
            foT2w_features = firstorder.RadiomicsFirstOrder(self.img.images[structure.BrainImageTypes.T2w],
                                                            self.img.images[structure.BrainImageTypes.BrainMask],
                                                            voxelBased=True)

            # Enable specified FO features for T2-weighted image
            foT2w_features.enabledFeatures = self.FO_features_parameters

            # Execute FO feature extraction on the T2-weighted image
            self.img.feature_images[FeatureImageTypes.T2w_FO] = foT2w_features.execute()

            # Combine individual FO features into a composite image for T2-weighted (if needed)
            composite_image_t2_fo = sitk.Compose(list(self.img.feature_images[FeatureImageTypes.T2w_FO].values()))

            # Copy information from the original T2-weighted image
            composite_image_t2_fo.CopyInformation(self.img.images[structure.BrainImageTypes.T2w])

            # Store the composite image for T2-weighted FO
            self.img.feature_images[FeatureImageTypes.T2w_FO] = composite_image_t2_fo

        # compute GLSZM features
        if self.GLSZM_features:

            # Enable GLSZM features based on the specified GLSZM feature parameters
            glszmT1w_features = glszm.RadiomicsGLSZM(self.img.images[structure.BrainImageTypes.T1w],
                                                     self.img.images[structure.BrainImageTypes.BrainMask],
                                                     voxelBased=True)

            # Print the GLSZM features that are in use
            print("GLSZM features in use:", [key for key, value in self.GLSZM_features_parameters.items() if value])

            # Enable specified GLSZM features
            glszmT1w_features.enabledFeatures = self.GLSZM_features_parameters

            # Execute GLSZM feature extraction on the T1-weighted image
            self.img.feature_images[FeatureImageTypes.T1w_GLSZM] = glszmT1w_features.execute()

            # Combine individual GLSZM features into a composite image (if needed)
            composite_image_t1_glszm = sitk.Compose(list(self.img.feature_images[FeatureImageTypes.T1w_GLSZM].values()))

            # Copy information from the original T1-weighted image
            composite_image_t1_glszm.CopyInformation(self.img.images[structure.BrainImageTypes.T1w])

            # Store the composite image for T1-weighted GLSZM
            self.img.feature_images[FeatureImageTypes.T1w_GLSZM] = composite_image_t1_glszm

            # Enable GLSZM features based on the specified GLSZM feature parameters for T2-weighted image
            glszmT2w_features = glszm.RadiomicsGLSZM(self.img.images[structure.BrainImageTypes.T2w],
                                                     self.img.images[structure.BrainImageTypes.BrainMask],
                                                     voxelBased=True)

            # Enable specified GLSZM features for T2-weighted image
            glszmT2w_features.enabledFeatures = self.GLSZM_features_parameters

            # Execute GLSZM feature extraction on the T2-weighted image
            self.img.feature_images[FeatureImageTypes.T2w_GLSZM] = glszmT2w_features.execute()

            # Combine individual GLSZM features into a composite image for T2-weighted (if needed)
            composite_image_t2_glszm = sitk.Compose(list(self.img.feature_images[FeatureImageTypes.T2w_GLSZM].values()))

            # Copy information from the original T2-weighted image
            composite_image_t2_glszm.CopyInformation(self.img.images[structure.BrainImageTypes.T2w])

            # Store the composite image for T2-weighted GLSZM
            self.img.feature_images[FeatureImageTypes.T2w_GLSZM] = composite_image_t2_glszm

        self._generate_feature_matrix()
        return self.img

    def _generate_feature_matrix(self):
        """Generates a feature matrix."""

        mask = None
        if self.training:
            # generate a randomized mask where 1 represents voxels used for training
            # the mask needs to be binary, where the value 1 is considered as a voxel which is to be loaded
            # we have following labels:
            # - 0 (background)
            # - 1 (white matter)
            # - 2 (grey matter)
            # - 3 (Hippocampus)
            # - 4 (Amygdala)
            # - 5 (Thalamus)

            # you can exclude background voxels from the training mask generation
            # mask_background = self.img.images[structure.BrainImageTypes.BrainMask]
            # and use background_mask=mask_background in get_mask()

            mask = fltr_feat.RandomizedTrainingMaskGenerator.get_mask(
                self.img.images[structure.BrainImageTypes.GroundTruth],
                [0, 1, 2, 3, 4, 5],
                [0.0003, 0.004, 0.003, 0.04, 0.04, 0.02])

            # convert the mask to a logical array where value 1 is False and value 0 is True
            mask = sitk.GetArrayFromImage(mask)
            mask = np.logical_not(mask)

        # Initialize an empty list to store processed image data
        image_data_list = []

        # Iterate over the feature images in the BrainImage instance
        print('----FEATURES CURRENTLY USED----')
        for feature_id, feature_image in self.img.feature_images.items():
            # Use the _image_as_numpy_array method to convert the feature image to a NumPy array
            feature_data = self._image_as_numpy_array(feature_image, mask)

            print(feature_id)
            # Append the processed feature data to the list
            image_data_list.append(feature_data)

        # Concatenate the processed feature data along the specified axis (axis=1)
        data = np.concatenate(image_data_list, axis=1)

        # generate features
        # data = np.concatenate(
        #     [self._image_as_numpy_array(image, mask) for id_, image in self.img.feature_images.items()],
        #     axis=1)

        # generate labels (note that we assume to have a ground truth even for testing)
        labels = self._image_as_numpy_array(self.img.images[structure.BrainImageTypes.GroundTruth], mask)

        self.img.feature_matrix = (data.astype(np.float32), labels.astype(np.int16))

    @staticmethod
    def _image_as_numpy_array(image: sitk.Image, mask: np.ndarray = None):
        """Gets an image as numpy array where each row is a voxel and each column is a feature.

        Args:
            image (sitk.Image): The image.
            mask (np.ndarray): A mask defining which voxels to return. True is background, False is a masked voxel.

        Returns:
            np.ndarray: An array where each row is a voxel and each column is a feature.
        """

        number_of_components = image.GetNumberOfComponentsPerPixel()  # the number of features for this image
        no_voxels = np.prod(image.GetSize())
        image = sitk.GetArrayFromImage(image)

        if mask is not None:
            no_voxels = np.size(mask) - np.count_nonzero(mask)

            if number_of_components == 1:
                masked_image = np.ma.masked_array(image, mask=mask)
            else:
                # image is a vector image, make a vector mask
                vector_mask = np.expand_dims(mask, axis=3)  # shape is now (z, x, y, 1)
                vector_mask = np.repeat(vector_mask, number_of_components,
                                        axis=3)  # shape is now (z, x, y, number_of_components)
                masked_image = np.ma.masked_array(image, mask=vector_mask)

            image = masked_image[~masked_image.mask]

        return image.reshape((no_voxels, number_of_components))


def pre_process(id_: str, paths: dict, **kwargs) -> structure.BrainImage:
    """Loads and processes an image.

    The processing includes:

    - Registration
    - Pre-processing
    - Feature extraction

    Args:
        id_ (str): An image identifier.
        paths (dict): A dict, where the keys are an image identifier of type structure.BrainImageTypes
            and the values are paths to the images.

    Returns:
        (structure.BrainImage):
    """

    print('-' * 10, 'Processing', id_)

    # load image
    path = paths.pop(id_, '')  # the value with key id_ is the root directory of the image
    path_to_transform = paths.pop(structure.BrainImageTypes.RegistrationTransform, '')
    img = {img_key: sitk.ReadImage(path) for img_key, path in paths.items()}
    transform = sitk.ReadTransform(path_to_transform)
    img = structure.BrainImage(id_, path, img, transform)

    # construct pipeline for brain mask registration
    # we need to perform this before the T1w and T2w pipeline because the registered mask is used for skull-stripping
    pipeline_brain_mask = fltr.FilterPipeline()
    if kwargs.get('registration_pre', False):
        pipeline_brain_mask.add_filter(fltr_prep.ImageRegistration())
        pipeline_brain_mask.set_param(fltr_prep.ImageRegistrationParameters(atlas_t1, img.transformation, True),
                                      len(pipeline_brain_mask.filters) - 1)

    # execute pipeline on the brain mask image
    img.images[structure.BrainImageTypes.BrainMask] = pipeline_brain_mask.execute(
        img.images[structure.BrainImageTypes.BrainMask])

    # construct pipeline for T1w image pre-processing
    pipeline_t1 = fltr.FilterPipeline()
    if kwargs.get('registration_pre', False):
        pipeline_t1.add_filter(fltr_prep.ImageRegistration())
        pipeline_t1.set_param(fltr_prep.ImageRegistrationParameters(atlas_t1, img.transformation),
                              len(pipeline_t1.filters) - 1)
    if kwargs.get('skullstrip_pre', False):
        pipeline_t1.add_filter(fltr_prep.SkullStripping())
        pipeline_t1.set_param(fltr_prep.SkullStrippingParameters(img.images[structure.BrainImageTypes.BrainMask]),
                              len(pipeline_t1.filters) - 1)
    if kwargs.get('normalization_pre', False):
        pipeline_t1.add_filter(fltr_prep.ImageNormalization())

    # execute pipeline on the T1w image
    img.images[structure.BrainImageTypes.T1w] = pipeline_t1.execute(img.images[structure.BrainImageTypes.T1w])

    # construct pipeline for T2w image pre-processing
    pipeline_t2 = fltr.FilterPipeline()
    if kwargs.get('registration_pre', False):
        pipeline_t2.add_filter(fltr_prep.ImageRegistration())
        pipeline_t2.set_param(fltr_prep.ImageRegistrationParameters(atlas_t2, img.transformation),
                              len(pipeline_t2.filters) - 1)
    if kwargs.get('skullstrip_pre', False):
        pipeline_t2.add_filter(fltr_prep.SkullStripping())
        pipeline_t2.set_param(fltr_prep.SkullStrippingParameters(img.images[structure.BrainImageTypes.BrainMask]),
                              len(pipeline_t2.filters) - 1)
    if kwargs.get('normalization_pre', False):
        pipeline_t2.add_filter(fltr_prep.ImageNormalization())

    # execute pipeline on the T2w image
    img.images[structure.BrainImageTypes.T2w] = pipeline_t2.execute(img.images[structure.BrainImageTypes.T2w])

    # construct pipeline for ground truth image pre-processing
    pipeline_gt = fltr.FilterPipeline()
    if kwargs.get('registration_pre', False):
        pipeline_gt.add_filter(fltr_prep.ImageRegistration())
        pipeline_gt.set_param(fltr_prep.ImageRegistrationParameters(atlas_t1, img.transformation, True),
                              len(pipeline_gt.filters) - 1)

    # execute pipeline on the ground truth image
    img.images[structure.BrainImageTypes.GroundTruth] = pipeline_gt.execute(
        img.images[structure.BrainImageTypes.GroundTruth])

    # update image properties to atlas image properties after registration
    img.image_properties = conversion.ImageProperties(img.images[structure.BrainImageTypes.T1w])

    # extract the features
    feature_extractor = FeatureExtractor(img, **kwargs)
    img = feature_extractor.execute

    img.feature_images = {}  # we free up memory because we only need the img.feature_matrix
    # for training of the classifier

    return img


def post_process(img: structure.BrainImage, segmentation: sitk.Image, probability: sitk.Image,
                 **kwargs) -> sitk.Image:
    """Post-processes a segmentation.

    Args:
        img (structure.BrainImage): The image.
        segmentation (sitk.Image): The segmentation (label image).
        probability (sitk.Image): The probabilities images (a vector image).

    Returns:
        sitk.Image: The post-processed image.
    """

    print('-' * 10, 'Post-processing', img.id_)

    # construct pipeline
    pipeline = fltr.FilterPipeline()
    if kwargs.get('simple_post', False):
        pipeline.add_filter(fltr_postp.ImagePostProcessing())
    if kwargs.get('crf_post', False):
        pipeline.add_filter(fltr_postp.DenseCRF())
        pipeline.set_param(fltr_postp.DenseCRFParams(img.images[structure.BrainImageTypes.T1w],
                                                     img.images[structure.BrainImageTypes.T2w],
                                                     probability), len(pipeline.filters) - 1)

    return pipeline.execute(segmentation)


def init_evaluator() -> eval_.Evaluator:
    """Initializes an evaluator.

    Returns:
        eval.Evaluator: An evaluator.
    """

    # initialize metrics
    metrics = [metric.DiceCoefficient(), metric.HausdorffDistance(95)]
    # warnings.warn('Initialized evaluation with the Dice coefficient. Do you know other suitable metrics?')

    # define the labels to evaluate
    labels = {1: 'WhiteMatter',
              2: 'GreyMatter',
              3: 'Hippocampus',
              4: 'Amygdala',
              5: 'Thalamus'
              }

    evaluator = eval_.SegmentationEvaluator(metrics, labels)
    return evaluator


def pre_process_batch(data_batch: t.Dict[structure.BrainImageTypes, structure.BrainImage],
                      pre_process_params: dict = None, multi_process: bool = True) -> t.List[structure.BrainImage]:
    """Loads and pre-processes a batch of images.

    The pre-processing includes:

    - Registration
    - Pre-processing
    - Feature extraction

    Args:
        data_batch (Dict[structure.BrainImageTypes, structure.BrainImage]): Batch of images to be processed.
        pre_process_params (dict): Pre-processing parameters.
        multi_process (bool): Whether to use the parallel processing on multiple cores or to run sequentially.

    Returns:
        List[structure.BrainImage]: A list of images.
    """
    if pre_process_params is None:
        pre_process_params = {}

    params_list = list(data_batch.items())
    if multi_process:
        images = mproc.MultiProcessor.run(pre_process, params_list, pre_process_params, mproc.PreProcessingPickleHelper)
    else:
        images = [pre_process(id_, path, **pre_process_params) for id_, path in params_list]
    return images


def post_process_batch(brain_images: t.List[structure.BrainImage], segmentations: t.List[sitk.Image],
                       probabilities: t.List[sitk.Image], post_process_params: dict = None,
                       multi_process: bool = True) -> t.List[sitk.Image]:
    """ Post-processes a batch of images.

    Args:
        brain_images (List[structure.BrainImageTypes]): Original images that were used for the prediction.
        segmentations (List[sitk.Image]): The predicted segmentation.
        probabilities (List[sitk.Image]): The prediction probabilities.
        post_process_params (dict): Post-processing parameters.
        multi_process (bool): Whether to use the parallel processing on multiple cores or to run sequentially.

    Returns:
        List[sitk.Image]: List of post-processed images
    """
    if post_process_params is None:
        post_process_params = {}

    param_list = zip(brain_images, segmentations, probabilities)
    if multi_process:
        pp_images = mproc.MultiProcessor.run(post_process, param_list, post_process_params,
                                             mproc.PostProcessingPickleHelper)
    else:
        pp_images = [post_process(img, seg, prob, **post_process_params) for img, seg, prob in param_list]
    return pp_images
