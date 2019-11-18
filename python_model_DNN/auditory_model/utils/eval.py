"""
Various functions for model evaluation.
"""

import numpy as np
import pandas as pd

from utils.load_data_raw import DataGenerator_raw
from utils.custom_loss import angle_diff_deg
from utils.plot import plot_history


def model_complete_eval(model, history, part_test, params, batch_size=1024,
                        add_metrics = [], workers=4):
    """
    Evaluate a specified model over all listining positions. Show model
    topology, training history and loss on test data set.
    Returns the DataGenerator object.

    Parameters
    ----------
    model : Keras model
        The model to evaluate.
    history : dict
        Dictionary containing the train history. History.history as
        returned by Keras model.fit() function.
    part_test : list 
        List containing the test set/partition.
    params : dict
        Dictionary containing the parameters for the DataGenerator
        object.
    batch_size : int, optional
        Batch size. Defaults to 1024.
    add_metrics : list, optional
        Add metrics in list to Keras model to evaluate its performance.
    workers : int, optional
        Number of workers for the multiprocessing functionalities of
        the Keras model methods. Defauts to 4.
        
    Returns
    -------
    b_gen : DataGenerator object
        DataGenerator object for the model to evaluate.
    """
    
    # get metrics from history dict
    metrics, v_met, n = get_history_metrics(history)
    # show model/net topology
    model.summary()
    
    # recompile model with additional metrics
    if add_metrics:
        add_metrics = model_add_metrics(model, add_metrics)
    else:
        add_metrics = metrics
    
    # evaluate model
    # create batch generator based on params dict
    params['batch_size'] = batch_size
    b_gen = DataGenerator_raw(part_test, **params)
    score = model_eval(model, b_gen, add_metrics, workers)

    # plot train history
    for j in range(n):
        plot_history(history[metrics[j]], history[v_met[j]], metrics[j])  
    return b_gen


def model_eval_pos(model, history, part_test, params, ID_ref, batch_size=1000, workers=4):
    """
    Evaluate a specified model over for each position individually.
    Show model topology, training history and loss on test data set.

    Parameters
    ----------
    model : Keras model
        The model to evaluate.
    history : dict
        Dictionary containing the train history. History.history as
        returned by Keras model.fit() function.
    part_test : list 
        List containing the test set/partition.
    params : dict
        Dictionary containing the parameters for the DataGenerator
        object.
    ID_ref : pandas DataFrame object
        DataFrame object containing the global ID reference list.
    batch_size : int, optional
        Batch size. Defaults to 1000.
    workers : int, optional
        Number of workers for the multiprocessing functionalities of
        the Keras model methods. Defauts to 4.
        
    Returns
    -------
    mae_p : ndarray
        Array containing the mean absolute error (or the loss metric)
        per position.
    mse_p : ndarray
        Array containing the mean squared error (or the first metric)
        per position.
    loc_pred : ndarray
        Array containing model predictions per position.
    """

    # get metrics from history dict
    metrics, _, _ = get_history_metrics(history)
    # show model/net topology
    model.summary()
    
    il = np.min(part_test)
    iu = np.max(part_test)
    ID = {}
    pos_str = ['pos0', 'pos1', 'pos2', 'pos3', 'pos4', 'pos5', 'pos6', 'pos7',
               'pos8', 'pos9']
    n_pos = len(pos_str)
    for i,s in enumerate(pos_str):
        ID[s] = ID_ref[il:iu+1].loc[ID_ref['pos_id'] == i].index.values
    
    mae_p = np.zeros(n_pos)
    mse_p = np.zeros(n_pos)
    loc_pred = np.zeros([n_pos,len(ID[pos_str[0]])])
    for i,s in enumerate(pos_str):
        params['batch_size'] = batch_size
        b_gen = DataGenerator_raw(ID[s], **params)
        mae_p[i], mse_p[i] = model.evaluate_generator(b_gen, verbose=0, 
                                                     use_multiprocessing=True,
                                                      workers=4)
        lpred = model.predict_generator(b_gen,verbose=0,
                                        use_multiprocessing=True,
                                        workers=4)
        loc_pred[i] = lpred.T
        print(s+' : ')
        print(mae_p[i])
    return mae_p, mse_p, loc_pred


def model_eval(model, b_gen, metric_str, workers=4):
    """
    Evaluate model on data generator.
    Prints and returns scores for specified metrics.

    Parameters
    ----------
    model : Keras model
        The model to evaluate.
    b_gen : DataGenerator object
        DataGenerator object to use for loading the data.
    metric_str : list of str 
        List of names of the metrics to evaluate. For printing.
    workers : int, optional
        Number of workers for the multiprocessing functionalities of
        the Keras model methods. Defauts to 4.
        
    Returns
    -------
    score : ndarray
        Array containing results of the evaluated metrics as returned
        by Keras model.evaluate() methods.
    """
    
    print('\nModel Evaluation: \n')
    score = model.evaluate_generator(b_gen, verbose=1,
                                     use_multiprocessing=True,
                                     workers=workers)
    for i, m in enumerate(metric_str):
        print('Test '+m+':', score[i])
    return score


def model_pred_on_gen_batch(model, b_gen, b_idx=0):
    """
    Predict on model for single batch returned from a data generator.
    Returns predictions as well as corresponding targets.
    """
    
    # predict on model
    X,y = b_gen.__getitem__(b_idx)
    pred = model.predict_on_batch(X)
    return pred, y


def calc_errors_m(model, part_x, params, pos_ids, verbose=0, workers=4):
    """
    Error analysis based on mean squared error.

    Parameters
    ----------
    model : Keras model
        The model to evaluate.
    part_x : list of ndarray
        List of arrays containing the test sets/partitions
        corresponding to only one position based on the ordering of
        pos_ids.
    params : dict
        Dictionary containing the parameters for the DataGenerator
        object.
    pos_ids : ndarray
        Array containing position ids.
    verbose : int, optional
        Verbose parameter for Keras model methods. Either 0, 1 or 2.
        Defaults to 0.
    workers : int, optional
        Number of workers for the multiprocessing functionalities of
        the Keras model methods. Defauts to 4.
        
    Returns
    -------
    MSE_m : float
        Mean squared error of particular method.
    tau_sq_m : float
        Systematic deviations a.k.a. bias for each position.
    sigma_sq_m : float
        Stochastic variations / variance.
    delta_x : float
        delta_x.
    delta_mean_x : float
        delta_mean_x.
    """

    # initialization
    L = 20 # 20 subjects
    B = 3600 # 360 angle * 10 repitions
    X = pos_ids.shape[0] # 10 positions
    delta_x = []
    b_gen = []
    delta_mean_x = np.zeros(X)
    sigma_sq_m = []
    
    # DELTA_l,m_b(x)
    for x in pos_ids:
        b_gen.append(DataGenerator_raw(part_x[x], **params))
        y_x = get_y_gen(b_gen[x])
        pred_x = model.predict_generator(b_gen[x], verbose=verbose,
                                         use_multiprocessing=True,
                                         workers=workers,
                                         max_queue_size=1000)
        delta = np.zeros(part_x[x].shape[0])
        for i in np.arange(part_x[x].shape[0]):
            delta[i] = angle_diff_deg(pred_x[i], y_x[i])
        delta_x.append(delta)

    # DELTA_MEAN_m(x)
    for x in pos_ids:
        delta_mean_x[x] = np.sum(delta_x[x]) / (L * B)
        # delta_mean_x[x] = np.mean(delta_x[x])
    
    # mean Square Error of particular method
    MSE_m = np.sum(np.square(delta_x)) / (L * B * X)
    # systematic deviations a.k.a. bias for each position
    tau_sq_m = np.sum(np.square(delta_mean_x)) / X
    # stochastic variations / variance
    for x in pos_ids:
        sigma_sq_m.append(delta_x[x] - delta_mean_x[x])
    sigma_sq_m = np.sum(np.square(sigma_sq_m)) / (L * B * X)
    return MSE_m, tau_sq_m, sigma_sq_m, delta_x, delta_mean_x


def get_y_gen(b_gen):
    """
    Gets and returns all targets from data generator.
    """
    
    l = b_gen.__len__()
    y = np.array([])
    for b_idx in range(l):
        _,y_t = b_gen.__getitem__(b_idx)
        y = np.append(y,y_t)
    return y


def create_test_params(feature_data, target_data, par, batch_size=1024,
                       shuffle=False):
    """
    Create and return a parameter dict for a DataGenerator object.
    """
    
    # check if data is a pandas DataFrame object
    if isinstance(feature_data, pd.DataFrame):
        feature_data = feature_data.values
    if isinstance(target_data, pd.DataFrame):
        target_data = target_data.values
    # create params dict
    params = {'dim': feature_data.shape[1],
              'batch_size': batch_size,
              'feature_data': feature_data,
              'target_data' : target_data,
              'shuffle': shuffle,
              'n_frames': par['nFrames'].values,
              'n_angles': par['nAngles'].values
             }
    return params


def get_history_metrics(history):
    """
    Get metrics from History.history dict as returned by Keras model
    fit/fit_generator functions.
    """
    
    metrics = list(history.keys())
    v_met = [x for x in metrics if 'val' in x]
    n = len(v_met)
    metrics = metrics[n:]
    return metrics, v_met, n


def model_add_metrics(model, add_metrics):
    """
    Recompiling a keras model with additional metrics for evaluation
    without affecting model weights. Returns list strings containing
    the metric names.
    """
    
    # assure list of unique metrics
    metrics = list(set(model.metrics+add_metrics))
    # recompile
    model.compile(optimizer=model.optimizer, loss=model.loss, metrics=metrics)
    # create list of strings of metrics for later evaluation; include loss metric
    metrics = [model.loss] + metrics
    metrics_str = [metrics[i].__name__ if callable(metrics[i]) else metrics[i] for i in range(len(metrics))]
    return metrics_str