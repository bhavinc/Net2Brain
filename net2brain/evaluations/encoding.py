import glob
import os
from tqdm import tqdm
import numpy as np
import random
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.decomposition import IncrementalPCA
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr, ttest_1samp

def get_layers_ncondns(feat_path):
    """Function to return facts about the npz-file

    Returns:
        num_layers (int): Amount of layers
        layer_list (list): List of layers
        num_conds (int): Amount of images

    """
    activations = glob.glob(feat_path + "/*.npz")
    num_condns = len(activations)
    feat = np.load(activations[0], allow_pickle=True)

    num_layers = 0
    layer_list = []

    for key in feat:
        if "__" in key:  # key: __header__, __version__, __globals__
            continue
        else:
            num_layers += 1
            layer_list.append(key)  # collect all layer names

    # List: ['conv1', 'conv2', 'conv3', 'conv4', 'conv5', 'fc6', 'fc7', 'fc8']

    return num_layers, layer_list, num_condns

def encode_layer(layer_id, n_components, batch_size, trn_Idx, tst_Idx, feat_path):
    activations = []
    feat_files = glob.glob(feat_path+'/*.npz')
    feat_files.sort()
    pca = IncrementalPCA(n_components=n_components, batch_size=batch_size)
    # Train pca encoding
    for jj,ii in enumerate(tqdm(trn_Idx)):  # for each datafile for the current layer
        feat = np.load(feat_files[ii], allow_pickle=True)  # get activations of the current layer
        activations.append(feat[layer_id].flatten())  # collect in a list
        if ((jj+1) % batch_size) == 0:
            pca.partial_fit(np.stack(activations[-batch_size:],axis=0))
    # Get the trn pca encoding
    pca_trn = pca.transform(np.stack(activations,axis=0))
    # Get the tst pca encoding
    activations = []
    for ii in tqdm(tst_Idx):  # for each datafile for the current layer
        feat = np.load(feat_files[ii], allow_pickle=True)  # get activations of the current layer
        activations.append(feat[layer_id].flatten())  # collect in a list
    pca_tst = pca.transform(np.stack(activations,axis=0))
    return pca_trn,pca_tst


def train_regression_per_ROI(trn_x,tst_x,trn_y,tst_y):
    reg = LinearRegression().fit(trn_x, trn_y)
    y_prd = reg.predict(tst_x)
    if tst_y == []:
        return y_prd
    correlation_lst = np.zeros(y_prd.shape[1])
    for v in tqdm(range(y_prd.shape[1])):
        correlation_lst[v] = pearsonr(y_prd[:,v], tst_y[:,v])[0]
    return correlation_lst

def linear_encoding(feat_path, roi_path, model_name, trn_tst_split=0.8, n_folds=3, n_components=100, batch_size=100, just_corr=True, return_correlations = False,random_state=14):
    fold_dict = {}
    corr_dict = {}
    model_name = os.path.basename(feat_path)
    feat_files = glob.glob(feat_path+'/*.npz')
    num_layers, layer_list, num_condns = get_layers_ncondns(feat_path)
    for fold_ii in range(n_folds):
        np.random.seed(fold_ii+random_state)
        random.seed(fold_ii+random_state)
        print('fold '+str(fold_ii+1)+'/'+str(n_folds))
        trn_Idx,tst_Idx = train_test_split(range(len(feat_files)),test_size=(1-trn_tst_split),train_size=trn_tst_split,random_state=fold_ii+random_state)
        #print(np.sum(tst_Idx))
        for layer_id in layer_list:
            if layer_id not in fold_dict.keys():
                fold_dict[layer_id] = {}
                corr_dict[layer_id] = {}
            pca_trn,pca_tst = encode_layer(layer_id, n_components, batch_size, trn_Idx, tst_Idx, feat_path)
            roi_files = glob.glob(roi_path+'/*.npy')
            for roi_file in roi_files:
                roi_name = os.path.basename(roi_file)[:-4]
                if roi_name not in fold_dict[layer_id].keys():
                    fold_dict[layer_id][roi_name] = []
                    corr_dict[layer_id][roi_name] = []
                fmri_data = np.load(os.path.join(roi_file))
                fmri_trn,fmri_tst = fmri_data[trn_Idx],fmri_data[tst_Idx]
                r_lst = train_regression_per_ROI(pca_trn,pca_tst,fmri_trn,fmri_tst)
                r = np.mean(r_lst)
                if return_correlations:                   
                    corr_dict[layer_id][roi_name].append(r_lst)
                    if fold_ii == n_folds-1:
                        corr_dict[layer_id][roi_name] = np.mean(np.array(corr_dict[layer_id][roi_name], dtype=np.float16),axis=0)
                    fold_dict[layer_id][roi_name].append(r)
    all_rois_df = pd.DataFrame(columns=['ROI', 'Layer', "Model", 'R', '%R2', 'Significance', 'SEM', 'LNC', 'UNC'])
    for layer_id,layer_dict in fold_dict.items():
        for roi_name,r_lst in layer_dict.items():
            significance = ttest_1samp(r_lst, 0)[1]
            R = np.mean(r_lst)
            output_dict = {"ROI":roi_name,
            "Layer": layer_id,
            "Model": model_name,
            "R": [R],
            "%R2": [np.nan],
            "Significance": [significance],
            "SEM": [np.nan],
            "LNC": [np.nan],
            "UNC": [np.nan]}
            layer_df = pd.DataFrame.from_dict(output_dict)
            all_rois_df = pd.concat([all_rois_df, layer_df], ignore_index=True)
    if return_correlations:
        return all_rois_df,corr_dict
    return all_rois_df


def test_encode_layer(layer_id, n_components, batch_size, trn_feat_path, tst_feat_path):
    activations = []
    feat_files = glob.glob(trn_feat_path+'/*.npz')
    feat_files.sort()
    tst_feat_files = glob.glob(tst_feat_path+'/*.npz')
    tst_feat_files.sort()
    pca = IncrementalPCA(n_components=n_components, batch_size=batch_size)
    # Train pca encoding
    for jj,ii in enumerate(tqdm(len(feat_files))):  # for each datafile for the current layer
        feat = np.load(feat_files[ii], allow_pickle=True)  # get activations of the current layer
        activations.append(feat[layer_id].flatten())  # collect in a list
        if ((jj+1) % batch_size) == 0:
            pca.partial_fit(np.stack(activations[-batch_size:],axis=0))
    # Get the trn pca encoding
    pca_trn = pca.transform(np.stack(activations,axis=0))
    # Get the tst pca encoding
    activations = []
    for ii in tqdm(len(tst_feat_files)):  # for each datafile for the current layer
        feat = np.load(tst_feat_files[ii], allow_pickle=True)  # get activations of the current layer
        activations.append(feat[layer_id].flatten())  # collect in a list
    pca_tst = pca.transform(np.stack(activations,axis=0))
    return pca_trn,pca_tst

def test_linear_encoding(trn_feat_path, tst_feat_path, roi_path, n_components=100, batch_size=100, random_state=14):
    fold_dict = {}
    corr_dict = {}
    model_name = os.path.basename(trn_feat_path)
    trn_feat_files = glob.glob(trn_feat_path+'/*.npz')
    tst_feat_files = glob.glob(tst_feat_path+'/*.npz')
    num_layers, layer_list, num_condns = get_layers_ncondns(feat_path)
    for fold_ii in range(1):
        np.random.seed(fold_ii+random_state)
        random.seed(fold_ii+random_state)
        #trn_Idx,tst_Idx = train_test_split(range(len(feat_files)),test_size=(1-trn_tst_split),train_size=trn_tst_split,random_state=fold_ii+random_state)
        #print(np.sum(tst_Idx))
        for layer_id in layer_list:
            if layer_id not in fold_dict.keys():
                fold_dict[layer_id] = {}
                corr_dict[layer_id] = {}
            pca_trn,pca_tst = encode_layer(layer_id, n_components, batch_size, trn_feat_path, tst_feat_path)
            roi_files = glob.glob(roi_path+'/*.npy')
            for roi_file in roi_files:
                roi_name = os.path.basename(roi_file)[:-4]
                if roi_name not in fold_dict[layer_id].keys():
                    fold_dict[layer_id][roi_name] = []
                    corr_dict[layer_id][roi_name] = []
                fmri_data = np.load(os.path.join(roi_file))
                fmri_trn = fmri_data
                r_lst = train_regression_per_ROI(pca_trn,pca_tst,fmri_trn,fmri_tst=[])                
                corr_dict[layer_id][roi_name].append(r_lst)
                corr_dict[layer_id][roi_name] = np.mean(np.array(corr_dict[layer_id][roi_name], dtype=np.float16),axis=0)
        return corr_dict
