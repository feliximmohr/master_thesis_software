"""
Python module that provides functions to split the dataset for training.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def create_split(ID_ref_t, cond_t, test_subset=[], valid_subset=[],
                 test_split=0.2, valid_split=0.2):
    """
    Create data set split based on the specified subsets. If either one
    or both subsets are empty or unspecified, split the remaining dataset
    randomly based on the specified proportions with sklearns
    train_test_split.
    
    Parameters
    ----------
    ID_ref_t : pandas DataFrame object
        DataFrame object containing the global ID reference list.
    cond_t : pandas.DataFrame object
        DataFrame object containing all conditions and corresponding
        indexes.
    test_subset : list of str
        List of strings containing position, condition or subject
        parameter substrings to select the subset to include in the
        test set, e.g. ['NFCHOA', 'pos1', 'subject_1'].
    valid_subset : list of str
        List of strings containing position, condition or subject
        parameter substrings to select the subset to include in the
        validation set, e.g. ['NFCHOA', 'pos1', 'subject_1'].
    test_split : float, int or None, optional
        Proportion of the data set to include in the test set, if no
        test_subset is provided.
    valid_split : float, int or None, optional
        Proportion of the data set to include in the validation set,
        if no valid_subset is provided.
        
    Returns
    -------
    partition : dict
        Dictionary that contains train, validation and test sets.
    """

    # Initialization
    partition = {'train':[], 'validation':[], 'test':[]}
    # only test on samples specified by test_subset
    cond_ids_test, pos_ids_test, sub_ids_test = get_subset_ids(test_subset,
                                                                   cond_t)
    # extract repective samples from ID_ref table
    list_IDs_test = get_subset_sample_idx(ID_ref_t, cond_ids_test,
                                          pos_ids_test, sub_ids_test)
    # only validate on samples specified by valid_subset
    cond_ids_valid, pos_ids_valid, sub_ids_valid = get_subset_ids(valid_subset,
                                                                  cond_t)
    # extract repective samples from ID_ref table
    list_IDs_valid = get_subset_sample_idx(ID_ref_t, cond_ids_valid,
                                           pos_ids_valid, sub_ids_valid)
    # only train on samples not part of test_subset or valid_subset
    idx_list = np.unique(np.concatenate((list_IDs_valid, list_IDs_test)))
    list_IDs = ID_ref_t.index.values.astype(np.uint32)
    list_IDs_train = np.delete(list_IDs, idx_list)
    
    # in case of no test_subset use sklearns train_test_split
    if not test_subset:
        list_IDs_train, list_IDs_test = train_test_split(list_IDs_train,
                                                         shuffle=True,
                                                         test_size=test_split)
    # in case of no valid_subset use sklearns train_test_split
    if not valid_subset:
        list_IDs_train, list_IDs_valid = train_test_split(list_IDs_train,
                                                          shuffle=True,
                                                          test_size=valid_split)


    # split data set in training, validation and test data
    partition['train'] = list_IDs_train
    partition['validation'] = list_IDs_valid
    partition['test'] = list_IDs_test
    return partition


def get_subset_ids(subset_list, cond_lookup_df, pos_lookup_df=None,
                   subject_lookup_df=None):
    """
    Get condition (cond_id), position (pos_id) and subject ids of a
    subset of the data specified by subset_list. Returns unique lists
    for cond_id, pos_id and subject_id, respectively.
    
    Parameters
    ----------
    subset_list : list
        List of strings containing position, condition or subject
        parameter substrings to select the subset,
        e.g. ['NFCHOA', 'pos1', 'subject_1']
    cond_lookup_df : pandas.DataFrame object
        DataFrame object containing all conditions and corresponding
        indexes.
    pos_lookup_df : pandas.DataFrame object
        Not yet supported.
    subject_lookup_df : pandas.DataFrame object
        Not yet supported.
        
    Returns
    -------
    cond_ids_subset : list
        List of condition ids of a subset as specified by subset_list.
    pos_ids_subset : list
        List of position ids of a subset as specified by subset_list.
    subject_ids_subset : list
        List of subject ids of a subset as specified by subset_list.
    """
    cond_ids_subset = []
    pos_ids_subset = []
    subject_ids_subset = []
    cond_id = []
    pos_id = []
    subject_id = []
    # do for each element in subset_list
    for elem in subset_list:
        # check if element related to positions, conditions or subjects
        if 'pos' in elem:
            pos_id = [int(elem[3:])-1]
        elif 'subject' in elem:
            subject_id = [int(elem[8:])]
        else:
            cond_id = cond_lookup_df.index[cond_lookup_df['sfs_method'].str.contains(elem)].tolist()
        # append to list
        pos_ids_subset.extend(pos_id)
        cond_ids_subset.extend(cond_id)
        subject_ids_subset.extend(subject_id)
    # return unique lists
    return list(set(cond_ids_subset)), list(set(pos_ids_subset)), list(set(subject_ids_subset))


def get_subset_sample_idx(ID_ref, cond_ids, pos_ids, subject_ids):
    """ 
    Get list of sample indices of a subset of the complete data set.
    The subset is selected by condition, position and subject ids.
    Returns a unique list of indices corresponding to exactly one 
    sample in the complete data set.
    
    Parameters
    ----------
    ID_ref : pandas DataFrame object
        DataFrame object containing the global ID reference list.
    cond_ids : list of int
        List of condition ids of a subset to select.
    pos_ids : list of int
        List of position ids of a subset to select.
    subject_ids : list of int
        List of subject ids of a subset to select.
        
    Returns
    -------
    idx_list : ndarray of uint32
        Numpy array containing the selected sample indices.
    """
    idx_list = np.array([],dtype=np.uint32)
    for pos in pos_ids:
        idx = ID_ref[(ID_ref.pos_id==pos)].index.values.astype(np.uint32)
        idx_list = np.concatenate((idx_list, idx))
    for cond in cond_ids:
        idx = ID_ref[(ID_ref.cond_id==cond)].index.values.astype(np.uint32)
        idx_list = np.concatenate((idx_list, idx))
    for sub in subject_ids:
        idx = ID_ref[(ID_ref.subject_id==sub)].index.values.astype(np.uint32)
        idx_list = np.concatenate((idx_list, idx))
    # Return unique idx list
    return np.unique(idx_list)


def get_pos_IDs(part, ID_ref, dictn=False):
    """
    Get list or dictionary containing all IDs in partition
    corresponding to one position.
    """

    if dictn:
        list_ID_x = {}
        pos = ['pos1','pos2','pos3','pos4','pos5','pos6','pos7','pos8','pos9','pos10']
        for i,s in enumerate(pos):
            list_ID_x[s] = ID_ref.iloc[part].loc[ID_ref['pos_id'] == i].index.values
    else:
        pos = np.unique(ID_ref['pos_id'].values)
        list_ID_x = []
        for i in pos:
            list_ID_x.append(ID_ref.iloc[part].loc[ID_ref['pos_id'] == i].index.values)
    return list_ID_x, pos