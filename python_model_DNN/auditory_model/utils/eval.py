"""
Various functions for model evaluation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.load_data_raw import DataGenerator_raw
from utils.custom_loss import angle_diff_deg

def model_complete_eval(model, history, part_test, params, batch_size=1024, workers=4):
    """Evaluate a specified model. Show model topology, training history and loss on test data set."""
    
    # Get metrics from history dict
    metrics, v_met, n = get_history_metrics(history)
    
    # Show model/net topology
    model.summary()

    # Evaluate model
    # create batch generator based on params dict
    params['batch_size'] = batch_size
    b_gen = DataGenerator_raw(part_test, **params)
    score = model_eval(model, b_gen, metrics, workers)

    # Plot train history
    for j in range(n):
        plot_history(history[metrics[j]], history[v_met[j]], metrics[j])
        
    return b_gen

def model_eval_pos(model, history, part_test, params, ID_ref, batch_size=1000, workers=4):
    """TODO"""
    # Get metrics from history dict
    metrics, _, _ = get_history_metrics(history)
    
    # Show model/net topology
    model.summary()
    
    il = np.min(part_test)
    iu = np.max(part_test)
    
    ID = {}
    pos_str = ['pos1','pos2','pos3','pos4','pos5','pos6','pos7','pos8','pos9','pos10']
    n_pos = len(pos_str)
    for i,s in enumerate(pos_str):
        ID[s] = ID_ref[il:iu+1].loc[ID_ref['pos_id'] == i].index.values
    
    mae_p = np.zeros(n_pos)
    mse_p = np.zeros(n_pos)
    loc_pred = np.zeros([n_pos,len(ID[pos_str[0]])])
    for i,s in enumerate(pos_str):
        params['batch_size'] = batch_size
        b_gen = DataGenerator_raw(ID[s], **params)
        mae_p[i], mse_p[i] = model.evaluate_generator(b_gen,verbose=0,use_multiprocessing=True, workers=4)
        lpred = model.predict_generator(b_gen,verbose=0,use_multiprocessing=True, workers=4)
        loc_pred[i] = lpred.T
        print(s+' : ')
        print(mae_p[i])
    
    return mae_p, mse_p, loc_pred

def model_eval(model, b_gen, metrics, workers=4):
    """
    Evaluate model on data generator.
    Prints and returns scores for specified metrics.
    """
    
    print('\nModel Evaluation: \n')
    score = model.evaluate_generator(b_gen, verbose=1, use_multiprocessing=True, workers=workers)
    for i, m in enumerate(metrics):
        print('Test '+m+':', score[i])
        
    return score

def model_pred_on_gen_batch(model, b_gen, b_idx=0):
    """
    Predict on model for single batch returned from a data generator.
    Returns predictions as well as corresponding targets.
    """
    
    #predict on model
    X,y = b_gen.__getitem__(b_idx)
    pred = model.predict_on_batch(X)
    return pred, y

def calc_errors_m(model, part_x, params, pos_ids, verbose=0, workers=4):
    """TODO."""
    L = 20 # 20 subjects
    B = 3600 # 360 angle * 10 repitions (?)
    X = pos_ids.shape[0] # 10 positions
    
    # Initialization
    delta_x = []
    b_gen = []
    delta_mean_x = np.zeros(X)
    sigma_sq_m = []
    
    #DELTA_l,m_b(x)
    for x in pos_ids:
        b_gen.append(DataGenerator_raw(part_x[x], **params))
        y_x = get_y_gen(b_gen[x])
        pred_x = model.predict_generator(b_gen[x],verbose=verbose,use_multiprocessing=True, workers=workers, max_queue_size=1000)
        delta = np.zeros(part_x[x].shape[0])
        for i in np.arange(part_x[x].shape[0]):
            delta[i] = angle_diff_deg(pred_x[i],y_x[i])
        delta_x.append(delta)

    #DELTA_MEAN_m(x)
    for x in pos_ids:
        delta_mean_x[x] = np.sum(delta_x[x]) / (L * B)
        #delta_mean_x[x] = np.mean(delta_x[x])
    
    # Mean Square Error of particular method
    MSE_m = np.sum(np.square(delta_x)) / (L*B*X)
    # systematic deviations a.k.a. bias for each position
    tau_sq_m = np.sum(np.square(delta_mean_x)) / X
    # stochastic variations / variance
    for x in pos_ids:
        sigma_sq_m.append(delta_x[x] - delta_mean_x[x])
    sigma_sq_m = np.sum(np.square(sigma_sq_m)) / (L*B*X)
    
    return MSE_m, tau_sq_m, sigma_sq_m, delta_x, delta_mean_x

def get_y_gen(b_gen):
    """
    TODO.
    """
    
    l = b_gen.__len__()
    y = np.array([])
    for b_idx in range(l):
        _,y_t = b_gen.__getitem__(b_idx)
        y = np.append(y,y_t)
    return y

def create_test_params(feature_data, target_data, par, batch_size=1024, shuffle=False):
    """Create and return a DataGenerator object."""
    
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
    """Get metrics from History.history dict as returned by Keras model fit/fit_generator functions."""
    metrics = list(history.keys())
    v_met = [x for x in metrics if 'val' in x]
    n = len(v_met)
    metrics = metrics[n:]
    return metrics, v_met, n

def plot_history(hist, val_hist, metric_str):
    """Plot train history."""
    plt.plot(hist)
    plt.plot(val_hist)
    plt.title('Model loss ('+metric_str+')')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.show()