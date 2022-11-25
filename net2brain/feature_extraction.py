from datetime import datetime
import glob
import os.path as op
import os
from PIL import Image

import numpy as np
import torch
from torch.autograd import Variable as V
import torchextractor as tx
from torchvision import transforms as T
from tqdm import tqdm

import net2brain.architectures.pytorch_models as pymodule
import net2brain.architectures.slowfast_models as pyvideo
import net2brain.architectures.taskonomy_models as taskonomy
import net2brain.architectures.timm_models as timm
import net2brain.architectures.torchhub_models as torchmodule
import net2brain.architectures.unet_models as unet
import net2brain.architectures.yolo_models as yolo


## Define relevant paths
CURRENT_DIR = op.abspath(os.curdir)
BASE_DIR = op.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = op.dirname(BASE_DIR)  # path to parent folder
FEATURES_DIR = op.join(PARENT_DIR, 'features')
GUI_DIR = op.join(BASE_DIR, 'helper', 'gui')
INPUTS_DIR = op.join(PARENT_DIR, 'input_data')
STIMULI_DIR = op.join(INPUTS_DIR, 'stimuli_data')
RDMS_DIR = op.join(PARENT_DIR, 'rdms')
BRAIN_DIR = op.join(INPUTS_DIR, 'brain_data')

## Get available networks
AVAILABLE_NETWORKS = {
    'standard': list(pymodule.MODELS.keys()),
    'timm': list(timm.MODELS.keys()),
    'pytorch': list(torchmodule.MODELS.keys()),
    'unet': list(unet.MODELS.keys()),
    'taskonomy': list(taskonomy.MODELS.keys()),
    'pyvideo': list(pyvideo.MODELS.keys())
}

try:
    import clip
    import architectures.clip_models as clip_models
    AVAILABLE_NETWORKS.update({'clip': list(clip_models.MODELS.keys())})
except ModuleNotFoundError:
    print("Clip models are not installed.")
    clip_exist = False

try:
    import cornet
    import architectures.cornet_models as cornet_models
    AVAILABLE_NETWORKS.update({'cornet': list(cornet_models.MODELS.keys())})
except ModuleNotFoundError:
    print("CORnet models are not installed.")
    cornet_exist = False

try:
    import vissl
    import architectures.vissl_models as vissl_models
    AVAILABLE_NETWORKS.update({'vissl': list(vissl_models.MODELS.keys())})
except ModuleNotFoundError:
    print("Vissl models are not installed")
    vissl_exist = False

try:
    import detectron2
    import architectures.detectron2_models as detectron2_models
    AVAILABLE_NETWORKS.update(
        {'detectron2': list(detectron2_models.MODELS.keys())}
    )
except ModuleNotFoundError:
    print("Detectron2 is not installed.")
    detectron_exist = False


def print_all_models():
    """Returns available models.

    Returns
    -------
    dict
        Available models by netset.
    """
    return AVAILABLE_NETWORKS


def print_all_netsets():
    """Returns available netsets.

    Returns
    -------
    list
       Available netsets.
    """
    return list(AVAILABLE_NETWORKS.keys())


def print_netset_models(netset):
    """Returns available models of a given netset.

    Parameters
    ----------
    netset : str
        Name of netset.

    Returns
    -------
    list
        Available models.

    Raises
    ------
    KeyError
        If netset is not available in the toolbox.
    """
    if netset in list(AVAILABLE_NETWORKS.keys()):
        return AVAILABLE_NETWORKS[netset]
    else:
        raise KeyError(
            f"This netset '{netset}' is not available. Available netsets are", 
            list(AVAILABLE_NETWORKS.keys())
        )


def find_model_like(name):
    """Find models containing the given string. Way of finding a model within \
        the model zoo.

    Parameters
    ----------
    name : str
        Name models.
    """
    for key, values in AVAILABLE_NETWORKS.items():
        for model_names in values:
            if name.lower() in model_names.lower():
                print(f'{key}: {model_names}')


class FeatureExtractor:
    # self.model = The actual model
    # self.model_name = Model name as string
    # self.device = GPU or CUDA
    # self.save_path = Location to save features
    # self.module = Where is our network-data located?
    # self.layers_to_extract= The layers we want to extract
    # self._extractor = If we want to use torchextractor or anything else
    # self._features_cleaner = Some extractions return the arrays in a weird format,
    #                        which is why some networks require a cleanup
    # self.transforms = Some images may need to be transformed/preprocessed before entering the network
    # self.preprocess = Function for preprocessing the images

    def __init__(self, model, device, netset=None, transforms=None):
        """Initializes feature extractor.

        Parameters
        ----------
        model : str or PyTorch model.
            If string is provided, the model will be loaded from the model zoo.
            Else the custom model will be used.
        device : str
            CPU or CUDA.
        netset : str optional
            NetSet from which to extract model, by default None.
        transforms : Pytorch Transforms, optional
            The transforms to be applied to the inputs, by default None.
        """
        # Set device
        self.device = device
        
        # Load model from netset or load custom model
        if type(model) == str:
            self.load_netset_model(model, netset)
        else: 
            self.load_model(model, transforms)

    def load_model(self, model, transforms=None):
        """Load a custom model.

        Parameters
        ----------
        model : PyTorch model
            Custom model.
        transforms : PyTorch Transforms, optional
             The transforms to be applied to the inputs, by default None.
        """
        self.model = model
        self.model.to(self.device)
        self.model_name = "Custom model"
        
        # Define preprocessing strategy
        self.transforms = transforms
        self.preprocess = self.preprocess_image
        
        # Define feature extraction parameters
        self.layers_to_extract = None
        self.features_path = None
        self._extractor = self._extract_features_tx
        self._features_cleaner = self._no_clean

    def load_netset_model(self, model_name, netset):
        """Load a model from the model zoo.

        Parameters
        ----------
        model_name : str
            Name of the model.
        netset : str
            Netset from which to extract the model.
        """
        self.model_name = model_name

        if netset == "standard":
            self.module = pymodule
            self.model = self.module.MODELS[model_name](pretrained=True)
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._no_clean

        elif netset == 'pytorch':
            self.module = torchmodule
            self.model = self.module.MODELS[model_name](
                'pytorch/vision:v0.10.0', self.model_name, pretrained=True
            )
            self.model.eval()
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._torch_clean

        elif netset == 'taskonomy':
            self.module = taskonomy
            self.model = self.module.MODELS[model_name](eval_only=True)
            checkpoint = torch.utils.model_zoo.load_url(
                self.module.MODEL_WEIGHTS[model_name]
            ) # Load weights
            self.model.load_state_dict(checkpoint['state_dict'])
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._no_clean

        elif netset == 'unet':
            self.module = unet
            self.model = self.module.MODELS[model_name](
                'mateuszbuda/brain-segmentation-pytorch', self.model_name, 
                in_channels=3, out_channels=1, init_features=32, 
                pretrained=True
            )
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._no_clean

        elif netset == 'clip':
            self.module = clip_models
            correct_model_name = self.model_name.replace("_-_", "/")
            self.model = self.module.MODELS[model_name](
                correct_model_name, device=self.device
            )[0]
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx_clip
            self._features_cleaner = self._no_clean

        elif netset == 'cornet':
            self.module = cornet_models
            self.model = self.module.MODELS[model_name]()
            self.model = torch.nn.DataParallel(self.model)
            ckpt_data = torch.utils.model_zoo.load_url(
                self.module.MODEL_WEIGHTS[model_name], map_location=self.device
            ) # Load weights
            self.model.load_state_dict(ckpt_data['state_dict'])
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._CORnet_RT_clean

        elif netset == 'yolo':
            # TODO: ONLY WORKS ON CUDA YET - NEEDS CLEANUP
            self.module = yolo
            self.model = self.module.MODELS[model_name](
                'ultralytics/yolov5', 'yolov5l', pretrained=True, 
                device=self.device
            )
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._no_clean

        elif netset == 'detectron2':
            self.module = detectron2_models
            config = self.module.configurator(self.model_name)
            self.model = self.module.MODELS[model_name](config)
            self.model.eval()
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._detectron_clean

        elif netset == 'vissl':
            self.module = vissl_models
            config = self.module.configurator(self.model_name)
            self.model = (
                self.module.MODELS[model_name]
                (config.MODEL, config.OPTIMIZER)
            )
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._no_clean

        elif netset == "timm":
            self.module = timm
            try:
                self.model = self.module.MODELS[model_name](
                    model_name, pretrained=True, features_only=True)
            except:
                self.model = self.module.MODELS[model_name](
                    model_name, pretrained=True)
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            if self.layers_to_extract == []:
                self._extractor = self._extract_features_timm
            else:
                self._extractor = self._extract_features_tx
            self._feature_cleaner = self._no_clean

        elif netset == 'pyvideo':
            self.module = pyvideo
            self.model = self.module.MODELS[model_name](
                'facebookresearch/pytorchvideo', self.model_name, 
                pretrained=True
            )
            self.model.eval()
            self.layers_to_extract = self.module.MODEL_NODES[model_name]
            self._extractor = self._extract_features_tx
            self._features_cleaner = self._slowfast_clean

        self.model.to(self.device)
        self.preprocess = self.module.preprocess

    def preprocess_image(self, image):
        """Default preprocessing based on ImageNet standard training.

        Parameters
        ----------
        image : str
            Path to the image to be preprocessed.

        Returns
        -------
        PyTorch Tensor
            Preprocessed image.
        """
        if self.transforms is None:
            self.transforms = T.Compose([
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        image = Image.open(image)
        image = V(self.transforms(image).convert('RGB').unsqueeze(0))
        image = image.to(self.device)
        return image

    def _extract_features_tx(self, image):
        """Extract features with torch extractor.

        Parameters
        ----------
        image : Torch Tensor
            Preprocessed image.

        Returns
        -------
        dict of Torch Tensors
            Features by layer.
        """
        extractor = tx.Extractor(self.model, self.layers_to_extract)
        _, features = extractor(image)
        features = self._features_cleaner(features)
        return features

    def _extract_features_tx_clip(self, image):
        """Extract CLIP features with torch extractor.

        Parameters
        ----------
        image : Torch Tensor
            Preprocessed image.

        Returns
        -------
        dict of Torch Tensors
            Features by layer.
        """
        extractor = tx.Extractor(self.model, self.layers_to_extract)
        image_data = image[0]
        tokenized_data = image[1]
        _, features = extractor(image_data, tokenized_data)
        features = self._features_cleaner(features)
        return features

    def _extract_features_timm(self, image):
        """Extract features with timm.

        Parameters
        ----------
        image : Torch Tensor
            Preprocessed image.

        Returns
        -------
        dict of Torch Tensors
            Features by layer.
        """
        features = self.model(image)
        # Convert the features into a dict because timm extractor returns a 
        # list of tensors
        converted_features = {}
        for counter, feature in enumerate(features):
            converted_features[f"feature {str(counter+1)}"] = feature.data.cpu()
        features = self._features_cleaner(converted_features)
        return converted_features

    def _no_clean(self, features):
        """Cleanup after feature extraction: This one requires no cleanup.
        Just put it on cpu in case it isn't yet!

        Args:
            features (dict:tensors): dictionary of tensors

        Returns:
            (dict:tensors): dictionary of tensors
        """
        return {key: value.data.cpu() for key, value in features.items()}

    def _torch_clean(self, features):
        """Cleanup function after feature extraction: This one contains subdictionaries which need to be eliminated

        Args:
            features (dict:tensors): dictionary of tensors

        Returns:
            (dict:tensors): dictionary of tensors
        """
        new_features = {}
        for key, value in features.items():
            try:
                new_features[key] = value["out"].data.cpu()
            except:
                new_features[key] = value.data.cpu()
        return new_features

    def _detectron_clean(self, features):
        """Cleanup function after feature extraction: This one contains subdictionaries which need to be eliminated

        Args:
            features (dict:tensors): dictionary of tensors

        Returns:
            (dict:tensors): dictionary of tensors
        """
        clean_dict = {}
        for key, subdict in features.items():
            keys = list(subdict.keys())
            for key in keys:
                clean_dict.update({key: subdict[key].cpu()})
        return clean_dict

    def _CORnet_RT_clean(self, features):
        """Cleanup function after feature extraction: The RT-Model contains subdirectories

        Args:
            features (dict:tensors): dictionary of tensors

        Returns:
            (dict:tensors): dictionary of tensors
        """

        if self.model_name == "cornet_rt":
            clean_dict = {}
            for A_key, subtuple in features.items():
                keys = [A_key + "_A", A_key + "_B"]
                for counter, key in enumerate(keys):
                    clean_dict.update({key: subtuple[counter].cpu()})
                    break  # we actually only want one key
            return clean_dict
        else:
            return {key: value.cpu() for key, value in features.items()}

    def _slowfast_clean(self, features):
        """Cleanup function after feature extraction: Some features have two values (list)

        Args:
            features (dict:tensors): dictionary of tensors

        Returns:
            (dict:tensors): dictionary of tensors
        """

        clean_dict = {}
        for A_key, subtuple in features.items():
            keys = [A_key + "_slow", A_key + "_fast"]

            try:  # if subdict is a list of two values
                for counter, key in enumerate(keys):
                    clean_dict.update({key: subtuple[counter].cpu()})
            except:
                clean_dict.update({A_key: subtuple.cpu()})

        return clean_dict

    def extract_from_images(self, image_list):
        """Function to loop over all our images, extract features and save them as .npz

        Args:
            image_list (list:str): List of paths to images
        """

        for image in tqdm(image_list):

            filename = op.split(image)[-1].split(".")[0]  # get filename

            # preprocess image
            processsed_image = self.preprocess(image, self.model_name)

            # extract features
            features = self.extractor(processsed_image)  # extract features

            # create save_path for file
            save_path = op.join(self.save_path, filename + ".npz")  # create safe-path

            # turn tensor into numpy array
            features = {key: value.detach().numpy() for key, value in features.items()}

            np.savez(save_path, **features)  # safe data

    def extract(self, dataset_path, save_path=None, layers_to_extract=None):
        """Function to start the feature extraction

        Args:
            layers (list): list of layers to extract
            dataset_path (path): path to dataset
            save_path (path): Path where to save features. Defaults to None.
        """

        # Create save path and ensure save path exists
        if save_path is None:
            self.save_path = _create_save_folder()
        else:
            _ensure_directory(save_path)
            self.save_path = save_path

        # Store layers in class
        if layers_to_extract is None:
            pass
        else:
            self.layers_to_extract = layers_to_extract

        # Find all input files
        image_list = glob.glob(op.join(dataset_path, "*"))
        image_list.sort()

        # get filetype
        filetype = op.split(image_list[0])[-1].split(".")[1]

        # If images are jpg, trigger the function
        if filetype == "jpg":
            self.extract_from_images(image_list)
        else:
            raise TypeError("Can only handle .jpg images for now")  # TODO: Add .png and .mp4 video data

    def get_all_layers(self):
        """Helping function to extract all possible layers from a model

        Returns:
            list: all layers we can extract features from
        """
        layers = tx.list_module_names(self.model)
        return layers


def _ensure_directory(path):
    """Ensure directory exists.

    Args:
        path (str): Path to folder that will be created.
    """
    if not os.path.exists(path):
        os.mkdir(path)


def _create_save_folder():
    """Creates folder to save the features in. They are structured after daytime

    Returns:
        save_path(str): Path to save folder
    """
    # Get current time
    now = datetime.now()
    now_formatted = now.strftime("%d.%m.%y %H:%M:%S")

    # Replace : through -
    log_time = now_formatted.replace(":", "-")

    # Combine to path
    save_path = f"features/{log_time}"

    # Create directory
    _ensure_directory(f"features/{log_time}")

    return save_path