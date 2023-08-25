

# Algonauts + Net2Brain CCN23 Hackathon 🧠

Welcome to __Net2Brain__, a powerful toolbox designed to facilitate the comparison of human brain activity patterns with the activations of Deep Neural Networks (DNNs). With over 600 pre-trained DNNs available, Net2Brain empowers neuroscientists to explore and analyze the relationships between artificial and biological neural representations.

Net2Brain is a collaborative effort between CVAI and Radek Cichy's lab, aimed at providing a user-friendly toolbox for neural research with deep neural networks.

## Hackathon Instructions
This workshop uses the Net2Brain Toolbox and a subset of the Algonauts challenge data to easily build predictive models of brain activity. To expedite the menial parts of the workshop we ask participants to pre-prepare their python environment. Participants working on their local machines will need to install the CCN23 branch of Net2Brain and download the data from the workshop google drive. If using a google Colab, please copy the iPython notebook from the workshop google drive and run the first command 10 minutes before the beginning of the workshop. This will install all relevant dependencies. Additionally, create a soft link to the data folder 'subj01' in your running directory (copying the data to your personal drive is unnecessary).

The following are the relevant links and commands:

- To install Net2Brain Locally:
   - pip install -U git+https://github.com/cvai-roig-lab/Net2Brain@CCN23

- Alternatively clone the repository and install the dependencies: 
   - git clone -b CCN23 https://github.com/cvai-roig-lab/Net2Brain.git
   - cd Net2Brain
   - pip install . 

- The workshop google drive: https://t.ly/jkIu-

- To create a soft link to the data in google drive (no need to copy data to your own drive): Shift+z

For any issues check the FAQ and Forum: https://groups.google.com/g/ccn23-algonauts-workshop/

## All-in-One Solution
Net2Brain offers an all-in-one solution by providing access to over 600 pretrained neural networks, specifically trained for various visual tasks. This extensive collection allows researchers to extract features from a diverse range of models, including pretrained and random architectures. Moreover, Net2Brain offers flexibility by allowing users to integrate their own models, thereby expanding the scope of experiments that can be conducted to evaluate brain responses.

## Bridging Neural and AI Research

One of the primary objectives of Net2Brain is to facilitate the collaboration between neural and AI research. By providing a user-friendly toolbox, we aim to bridge the gap and empower non-computer scientists to leverage the benefits of deep neural networks in their neuroscientific investigations.



# Key Functions

The toolbox encompasses several key functions to support comprehensive neural research:

1. __Feature Extraction__: Net2Brain enables the extraction of features from a vast collection of pretrained and random models, catering to a wide range of visual tasks. It also provides the flexibility to extract features from your own custom models, allowing you to tailor the analysis to your specific research needs.

2. __Creation of Representational Dissimilarity Matrices (RDMs)__: Users can generate RDMs to analyze the dissimilarity between neural representations.

3. __Evaluation__: Net2Brain incorporates Representational Similarity Analysis (RSA) ([Kriegeskorte et al., 2008](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2605405/)) techniques, including weighted RSA and Searchlight evaluation, to compare neural representations with brain activity patterns.

4. __Plotting__: Net2Brain provides plotting functionalities that allow you to visualize and present your analysis results in a polished manner. The generated plots are designed to be publication-ready, making it easier for you to showcase your findings and share them with the scientific community.


# Model Taxonomy

__Net2Brain__ provides a comprehensive model taxonomy system to assist users in selecting the most suitable models for their studies. This taxonomy system classifies models based on attributes such as dataset, training method, and visual task. Let's take a look at an example that showcases the usage of the taxonomy system:

```python
from net2brain.feature_extraction import show_taxonomy
from net2brain.feature_extraction import find_model_by_dataset
from net2brain.feature_extraction import find_model_by_training_method
from net2brain.feature_extraction import find_model_by_visual_task
from net2brain.feature_extraction import find_model_by_custom

# Show the taxonomy
show_taxonomy()

# Find models based on dataset
find_model_by_dataset("Taskonomy")

# Find models based on training method
find_model_by_training_method("SimCLR")

# Find models based on visual task
find_model_by_visual_task("Panoptic Segmentation")

# Find models based on custom attributes
find_model_by_custom(["COCO", "Object Detection"], model_name="fpn")
```

This taxonomy system provides a convenient way to search for models that align with specific research requirements.


# Example Notebooks and Datasets

Net2Brain provides a set of [example notebooks](notebooks) that demonstrate the various functionalities of the toolbox. These notebooks are designed to guide users through the process of model taxonomy exploration, feature extraction, RDM creation, and evaluation. 

To further facilitate your exploration, we also offer pre-downloaded datasets that you can use in conjunction with the example notebooks. These datasets allow you to immediately dive into the experimentation process and gain hands-on experience with Net2Brain. Simply follow the instructions provided in the notebooks to access and utilize the datasets effectively.



# Compatibility and System Requirements

Net2Brain has been extensively tested on all systems running Python version up to 3.10. It is compatible with major operating systems, including Windows, macOS, and Linux.

Please note that there are two netsets, Detectron2 and VISSL, which are specifically designed for Linux-based systems. Installation instructions for these netsets can be found in the provided notebooks.

# Installation

To install Net2Brain and its dependencies, please follow these steps:

1. Install the repository on your machine. You can use the following command in your terminal:

```
pip install -U git+https://github.com/cvai-roig-lab/Net2Brain
```

2. Once the installation is complete, you can import Net2Brain in your Python environment and start utilizing its powerful features for neural research.



# Examples of the Toolbox

## Feature Extraction

Net2Brain allows you to extract features from a variety of pretrained models or your own custom models. This feature extraction process is crucial for analyzing neural network representations and comparing them with human brain activity patterns.

To extract features using Net2Brain, follow these steps:

```python
from net2brain.feature_extraction import FeatureExtractor

# Initialize the FeatureExtractor with a pretrained model
fx = FeatureExtractor(model='AlexNet', netset='standard', device='cpu')

# Extract features from a dataset
fx.extract(dataset_path=stimuli_path, save_format='npz', save_path='AlexNet_Feat')
```
In this example, we use the FeatureExtractor class to extract features from the AlexNet model. The extracted features are saved in the specified format, such as NumPy .npz format, using the given save path.

Net2Brain provides flexibility in selecting models, choosing layers for feature extraction, and saving the extracted features. Refer to the provided notebooks and documentation for more detailed examples and customization options.


## Creating RDMs


After feature extraction, the next step is to create Representational Dissimilarity Matrices (RDMs) using Net2Brain's RDM Creator.

To generate RDMs, follow these steps:

```python
from net2brain.rdm_creation import RDMCreator

# Define the paths
feat_path = "AlexNet_Feat"
save_path = "AlexNet_RDM"

# Create an instance of RDMCreator
creator = RDMCreator(feat_path, save_path)

# Generate and save the RDMs
creator.create_rdms()
```
In this example, the RDMCreator class is used to create RDMs from previously extracted features using the AlexNet model. The extracted features are located at feat_path, and the resulting RDMs will be saved at save_path.

The RDM Creator calculates dissimilarities between neural representations of different images and generates RDMs with a shape of (#Images, #Images) for each specified layer. These RDMs provide insights into the similarities and differences in neural representations.

For more detailed instructions and customization options, refer to the provided notebooks and documentation.




## Evaluation: RSA and Plotting

Net2Brain provides powerful evaluation capabilities to analyze and compare the representations of neural networks. One of the key evaluation metrics available is RSA (Representational Similarity Analysis). Additionally, the toolbox offers integrated plotting functionality to visualize evaluation results.
RSA Evaluation

To perform RSA evaluation, follow these steps:

```python
from net2brain.evaluations.rsa import RSA
from net2brain.utils.download_datasets import load_dataset

# Load the ROIs
stimuli_path, roi_path = load_dataset("bonner_pnas2017")

# Define the paths to the model and brain RDMs
model_rdms = "AlexNet_RDM"
brain_rdms = roi_path

# Start RSA evaluation
evaluation_alexnet = RSA(model_rdms, brain_rdms, model_name="AlexNet")

# Evaluate and obtain a pandas DataFrame
dataframe1 = evaluation_alexnet.evaluate()

# Display the results
display(dataframe1)
```

## Plotting RSA Evaluation Results

The integrated plotting functionality of Net2Brain allows you to easily visualize the RSA evaluation results. To plot the data using a single DataFrame, use the following code:

```python
from net2brain.evaluations.plotting import Plotting

# Initialize the plotter with the DataFrame
plotter = Plotting([dataframe1])

# Plot the results
# Optionally, pass metrix='R' if you do not want to lot with R2
results_dataframe = plotter.plot()
```

Refer to the provided notebooks and documentation for detailed instructions on customizing RSA evaluation and exploring additional options offered by Net2Brain

## Linear Encoding

Another integrated analysis pipeline is a linear encoder. Given a npy file with voxel values, and extracted features, the encoder performs an X-fold regression where the training data is used to train a PCA embedding and a linear regression to predict voxel values. The output is the testing split X-fold average pearson correlation.

```python
from net2brain.evaluations.encoding import linear_encoding

# n_folds: number of folds
# trn_tst_split: how to split training and testing data at each fold
# n_components: number of PCA components
# batch_size: size of batch of updating the incremental pca
results_dataframe = linear_encoding(feature_path, roi_path, model_name, n_folds=3, trn_tst_split=0.8, n_components=100, batch_size=100)
```

# Contribution and Support

Net2Brain is an open-source project, and we welcome contributions from the community. If you encounter any issues, have suggestions for improvements, or would like to contribute to the project, feel free to write an issue or submit pull requests yourself.

For support, inquiries, or feedback, please reach out to us. You can find our contact information in the repository's documentation.

We hope Net2Brain proves to be a valuable resource in your neuroscientific investigations. Happy exploring!



## Contributors of Net2Brain

- B.Sc. Domenic Bersch
- Dr. Sari Saba-Sadiya
- M. Sc. Martina Vilas
- M. Sc. Timothy Schaumlöffel
- Dr. Kshitij Dwivedi
- Dr. Radoslaw Martin Cichy


## Citing Net2Brain
If you use Net2Brain in your research, please don't forget to cite us:
```bash
@misc{https://doi.org/10.48550/arxiv.2208.09677,
     doi = {10.48550/ARXIV.2208.09677},
     url = {https://arxiv.org/abs/2208.09677},
     author = {Bersch, Domenic and Dwivedi, Kshitij and Vilas, 
     Martina and Cichy, Radoslaw M. and Roig, Gemma},
     title = {Net2Brain: A Toolbox to compare artificial vision models 
     with human brain responses},
     publisher = {arXiv},
     year = {2022},
     copyright = {Creative Commons Attribution Non Commercial Share Alike 4.0 International}}
```


## References
This toolbox is inspired by the Algonauts Project and contains collections of artificial neural networks from different sources.

- **The Algonauts Project:** Radoslaw Martin Cichy, Gemma Roig, Alex Andonian, Kshitij Dwivedi, Benjamin Lahner, Alex Lascelles, Yalda Mohsenzadeh, Kandan Ramakrishnan, and Aude Oliva. (2019). The Algonauts Project: A Platform for Communication between the Sciences of Biological and Artificial Intelligence. arXiv, arXiv:1905.05675
- **The dataset provided in the library:** Radoslaw M. Cichy, Dimitrios Pantazis and Aude Oliva. (2016). Similarity-Based Fusion of MEG and fMRI Reveals Spatio-Temporal Dynamics in Human Cortex During Visual Object Recognition. Cerebral Cortex, 26 (8): 3563-3579.
- **RSA-Toolbox:** Nikolaus Kriegeskorte, Jörn Diedrichsen, Marieke Mur and Ian Charest (2019) The toolbox replaces the 2013 matlab version the toolbox of rsatoolbox previously at ilogue/rsatoolbox and reflects many of the new methodological developements. Net2Brain uses its functionality to perform "Weighted RSA".
- **PyTorch Models:** https://pytorch.org/vision/0.8/models.html
- **CORnet-Z and CORnet-RT:** Kubilius, J., Schrimpf, M., Nayebi, A., Bear, D., Yamins, D.L.K., DiCarlo, J.J. (2018) CORnet: Modeling the Neural Mechanisms of Core Object Recognition. biorxiv. doi:10.1101/408385
- **CORnet-S:** Kubilius, J., Schrimpf, M., Kar, K., Rajalingham, R., Hong, H., Majaj, N., ... & Dicarlo, J. (2019). Brain-like object recognition with high-performing shallow recurrent ANNs. In Advances in Neural Information Processing Systems (pp. 12785-12796).
- **MoCo:** Kaiming He and Haoqi Fan and Yuxin Wu and Saining Xie and Ross Girshick, Momentum Contrast for Unsupervised Visual Representation Learning (2019), arXiv preprint arXiv:1911.05722
- **SwAv:** Caron, Mathilde and Misra, Ishan and Mairal, Julien and Goyal, Priya and Bojanowski, Piotr and Joulin, Armand ,Unsupervised Learning of Visual Features by Contrasting Cluster Assignments (2020), Proceedings of Advances in Neural Information Processing Systems (NeurIPS)
- **Taskonomy:** Zamir, Amir R and Sax, Alexander and and Shen, William B and Guibas, Leonidas and Malik, Jitendra and Savarese, Silvio, Taskonomy: Disentangling Task Transfer Learning (2018), 2018 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)
- **Image Models:** Ross Wightman, PyTorch Image Models(2019), 10.5281/zenodo.4414861, https://github.com/rwightman/pytorch-image-models
- **Detectron2:** Yuxin Wu and Alexander Kirillov and Francisco Massa and Wan-Yen Lo and Ross Girshick, Detectron2 (2019), https://github.com/facebookresearch/detectron2
- **SlowFast:** Haoqi Fan and Yanghao Li and Bo Xiong and Wan-Yen Lo and Christoph Feichtenhofer, PySlowFast(2020), https://github.com/facebookresearch/slowfast
