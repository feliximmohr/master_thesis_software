"""
A python module that provides different custom loss functions.
"""

import tensorflow as tf
from keras import backend as K
from numpy import pi, sin, cos, rad2deg, deg2rad, arctan2

def mse_wrap_angle(y_true, y_pred):
    """
    Custom loss function based on MSE but with angles wrapped to 360 degree.
    Tensorflows atan2 is used. Therefore conversion to radiant and back is performed.
    """
    diff = tf_angle_diff_deg(y_pred, y_true)
    return K.mean(K.square(diff), axis=-1)

def mae_wrap_angle(y_true, y_pred):
    """
    Custom loss function based on MAE but with angles wrapped to 360 degree.
    Tensorflows atan2 is used. Therefore conversion to radiant and back is performed.
    """
    diff = tf_angle_diff_deg(y_pred, y_true)
    return K.mean(K.abs(diff), axis=-1)

def mae_wrap_angle_bound(y_true, y_pred):
    """
    Custom loss function based on MAE but with angles wrapped to 360 degree.
    Tensorflows atan2 is used. Therefore conversion to radiant and back is performed.
    """
    y_pred_neg = tf.math.negative(y_pred)
    cond = tf.math.logical_or(tf.math.greater(y_pred,180), tf.math.less(y_pred,-180))
    y_pred = tf.compat.v2.where(cond,y_pred_neg,y_pred)
    
    diff = tf_angle_diff_deg(y_pred, y_true)
    return K.mean(K.abs(diff), axis=-1)

def tf_angle_diff_deg(a,b):
    """Calculates angle differences in degrees in tensorflow."""
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

def angle_diff_deg(a,b):
    """Calculates angle differences in degrees for evaluation outside tensorflow."""
    a = deg2rad(a)
    b = deg2rad(b)
    diff = arctan2(sin(a - b), cos(a - b))
    return rad2deg(diff)