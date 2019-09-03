"""
A python module that provides different custom loss functions.
"""

import tensorflow as tf
from keras import backend as K
from numpy import pi

def mse_wrap_angle(y_true, y_pred):
    """
    Custom loss function based on MSE but with angles wrapped to 360 degree.
    Tensorflows atan2 is used. Therefore conversion to radiant and back is performed.
    """
    diff = angle_diff_deg(y_pred, y_true)
    return K.mean(K.square(diff), axis=-1)

def mae_wrap_angle(y_true, y_pred):
    """
    Custom loss function based on MAE but with angles wrapped to 360 degree.
    Tensorflows atan2 is used. Therefore conversion to radiant and back is performed.
    """
    diff = angle_diff_deg(y_pred, y_true)
    return K.mean(K.abs(diff), axis=-1)

def mse_wrap_angle_old(y_true, y_pred):
    """Custom loss function based on MSE but with angles wrapped to 360 degree. Not working."""
    diff = y_pred - y_true
    if K.greater(diff,180) is not None:
        diff = diff - 360
    elif K.less(diff,-180) is not None:
        diff = diff + 360
    return K.mean(K.square(diff), axis=-1)

def mae_wrap_angle_old(y_true, y_pred):
    """Custom loss function based on MAE but with angles wrapped to 360 degree. Not working."""
    diff = y_pred - y_true
    if K.greater(diff,180) is not None:
        diff = diff - 360
    elif K.less(diff,-180) is not None:
        diff = diff + 360
    return K.mean(K.abs(diff), axis=-1)

def angle_diff_deg(a,b):
    """Calculates angle differences in degrees."""
    a = tf_deg2rad(a)
    b = tf_deg2rad(b)
    diff = tf.atan2(tf.sin(a - b), tf.cos(a - b))
    return tf_rad2deg(diff)

def tf_deg2rad(a):
    """Tensorflow compatible conversion from degree to radians."""
    return tf.divide(tf.multiply(a,pi),180)

def tf_rad2deg(a):
    """Tensorflow compatible conversion from degree to radians."""
    return tf.divide(tf.multiply(a,180),pi)