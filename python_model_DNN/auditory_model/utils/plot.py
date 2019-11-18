"""
Various functions for plotting.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


def plot_history(hist, val_hist, metric_str):
    """Plot train and validation history."""
    plt.plot(hist)
    plt.plot(val_hist)
    plt.title('Model loss ('+metric_str+')')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    plt.show()
    

def plot_locaz_all(pred, y=None, l=False, title=None):
    """
    Plot localization azimuth prediction for all positions and
    optionally also corresponding ground truth for comparison.
    
    Parameters
    ----------
    pred : list of lists or list of ndarrays
        List of predicted localization azimuth data for all positions.
    y : list of lists or list of ndarrays, optional
        List of target or ground truth data for localization azimuth
        for all positions.
    l : bool, optional
        If True plot from -180<x<180 instead of 0<x<360.
        Defaults to False.
    title : string, optional
        Figure title.
    """
    n_pos = len(pred)
    
    fig = plt.figure()
    fig.suptitle(title, fontsize='x-large')

    if y is not None:
        gs0 = gridspec.GridSpec(n_pos, 1, figure=fig)
        for i in range(n_pos):
            gs00 = gs0[i].subgridspec(1, 21)
            _, _, _ = plot_locaz(pred[i], y[i], fig=fig, l=l,
                                 title='Position '+str(i), gs=(gs00[:,:9],
                                 gs00[:,10:19], gs00[:,20]))
    else:
        gs0 = gridspec.GridSpec(3, 4, figure=fig)
        for i in range(n_pos):
            gs00 = gs0[i].subgridspec(21, 21)
            _, ax, _ = plot_locaz(pred[i], fig=fig, l=l,
                                  title='Position '+str(i),
                                  gs=(gs00[:20,:20], gs00[0,0], gs00[0,0]))
            ax.set_xlabel('')
            ax.set_ylabel('')
            fig.legend(ax.get_children()[0:1],['predictions'],
                       loc='upper right', bbox_to_anchor=(0.8, 0.3))
    return fig
    

def plot_locaz(pred, y=None, l=False, title=None, fig=None, gs=None, b=10,
               s=20):
    """
    Plot localization azimuth prediction for one position and
    optionally also corresponding ground truth for comparison.
    
    Parameters
    ----------
    pred : list or ndarray
        Predicted localization azimuth data.
    y : list or ndarray, optional
        Target or ground truth data for localization azimuth.
    l : bool
        If True plot from -180<x<180 instead of 0<x<360.
        Defaults to False.
    title : string, optional
        Figure title.
    fig : Figure object, optional
        matplotlib.figure.Figure object.
    gs : Gridspec object, optional
        matplot.lib.gridspec.Gridspec object.
    b : int, optional
        Number of repititions. Defaults to 10.
    s : int, optional
        Number of subjects. Defaults to 20.
        
    Returns
    -------
    fig : Figure object
        matplotlib.figure.Figure object for later use.
    ax_p : Axes object
        matplotlib object for later use.
        
    """
    # Check optional input arguments
    if fig is None:
        fig = plt.figure()
    
    if gs is None:
        gs = gridspec.GridSpec(1,21)
        gs_p = gs[:,:9]
        gs_yc = gs[:,20]
        gs_y = gs[:,10:19]
        if y is None:
            gs_p = 111
    else:
        gs_p = gs[0]
        gs_yc = gs[2]
        gs_y = gs[1]
    
    # number of values y for exactly one data point x;
    # number of repitions * number of subjects
    n = b*s   
        
    # create subplots 
    ax_p = fig.add_subplot(gs_p)
    if y is not None:
        ax_yc = fig.add_subplot(gs_yc)
        ax_y = fig.add_subplot(gs_y, sharey=ax_p, sharex=ax_p)
    else:
        ax_y = 0
    
    # optionally change range
    if l:
        xl = np.kron(np.arange(180), np.ones(n))
        xu = np.kron(np.arange(-180,0), np.ones(n))
        x = np.concatenate((xl,xu))
        plt.xlim(-200,200)
        plt.ylim(-200,200)
    else:
        x =  np.kron(np.arange(360), np.ones(n))
        plt.xlim(-10,380)
        plt.ylim(-200,200)
        
    # plotting    
    ax_p.scatter(x,pred, color='b', marker='.', label='predictions')
    ax_p.set_ylabel('Localization Azimuth / deg')
    ax_p.set_xlabel('Head Rotation / deg')
    if title:
        ax_p.set_title(title)
    if y is not None:
        ax_y.scatter(x,y, color='c', marker = '.', label='human / gt')
        ax_y.set_xlabel('Head Rotation / deg')
        if title:
            ax_y.set_title(title)
        ax_yc.scatter(np.zeros(n),y[:n], marker='.', color='c')
        ax_yc.scatter([0],[np.mean(y[:n])],marker='+',color='r')
    
    # add grid and lines
    ax_p.grid(b=True, which='major', color='#999999', linestyle='-',
              alpha=0.2)
    ax_p.plot([-500,500],[180,180],color='k', alpha=0.3)
    ax_p.plot([-500,500],[-180,-180],color='k',alpha=0.3)
    ax_p.plot([180,180],[-500,500],color='r', alpha=0.1)
    ax_p.plot([-180,-180],[-500,500],color='r', alpha=0.1)
    ax_p.scatter([0],[np.mean(pred[:n])],marker='+',color='r')
    if y is not None:
        ax_y.grid(b=True, which='major', color='#999999', linestyle='-',
                  alpha=0.2)
        ax_y.plot([-500,500],[180,180],color='k', alpha=0.3)
        ax_y.plot([-500,500],[-180,-180],color='k',alpha=0.3)
        ax_y.plot([180,180],[-500,500],color='r', alpha=0.1)
        ax_y.plot([-180,-180],[-500,500],color='r', alpha=0.1)
        ax_y.scatter([0],[np.mean(y[:n])],marker='+',color='r')
        ax_yc.grid(b=True, which='major', color='#999999', linestyle='-',
                   alpha=0.2)
        ax_yc.set_xticklabels([])
    return fig, ax_p, ax_y


def get_model_info(filename):
    """
    Get model info from filename for pretty plotting.
    Parse filename and returns names of model, loss, test data,
    special training conditions, batch size and optimizer.
    """
    # parse filename
    parts = filename.split('_')
    model = parts[0]
    loss = parts[1]
    optim = parts[2]
    bs = parts[3][2:]
    tdata = parts[4].split('-')[1:]
    special = parts[5]
    
    # prettify info strings
    if '001' not in model:
        model = model + '-001'
    if 'maew'in loss:
        loss = 'mae-w'
    elif 'msew'in loss:
        loss = 'mse-w'
    for i,elem in enumerate(tdata):
        if 'NR'in elem:
            tdata[i] = 'NFCHOA_R'+elem[2:]
        elif 'NM'in elem:
            tdata[i] = 'NFCHOA_M'+elem[2:]
    if 'test' in special:
        special = ''
    elif 'nsc' in special:
        special = ' + features not scaled'
    elif 'reg' in special:
        special = ' + '+special.split('-')[1]+'-'+special.split('-')[2]
    else:
        special = ' + '+special
    return model, loss, tdata, special, bs, optim