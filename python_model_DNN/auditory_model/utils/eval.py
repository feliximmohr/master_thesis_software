"""
Various functions for model evaluation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from utils.load_data_raw import DataGenerator_raw

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

def create_test_params(feature_data, target_data, par, batch_size=1024, shuffle=False):
    """Create and return a DataGenerator object."""
    
    # check is data is a pandas DataFrame object
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