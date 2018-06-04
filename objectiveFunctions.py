# objective functions
import scipy.stats as sps
import numpy as np

def r2(x,y):
    # from: https://en.wikipedia.org/wiki/Coefficient_of_determination#As_explained_variance

    n = len(x)
    m = len(y)

    if np.sum(np.isnan(x)) == n or np.sum(np.isnan(y)) == m: return np.NaN

    yBar = np.nanmean(y)
    SStot = np.nansum(np.square(y-yBar)) # compute sum of squares total
    SSres = np.nansum(np.square(y-x)) # residual sum of squares
    
    return 1.-(SSres/SStot)

def NSE(x,y):
    # from: https://en.wikipedia.org/wiki/Nash%E2%80%93Sutcliffe_model_efficiency_coefficient

    n = len(x)
    m = len(y)

    if np.sum(np.isnan(x)) == n or np.sum(np.isnan(y)) == m: return np.NaN

    yBar = np.nanmean(y)
    return 1. - (np.nansum(np.square(x-y))/np.nansum(np.nanmean(y-yBar)))

def MAE(x,y):
    # from: https://en.wikipedia.org/wiki/Mean_absolute_error

    n = len(x)
    m = len(y)

    if np.sum(np.isnan(x)) == n or np.sum(np.isnan(y)) == m: return np.NaN

    return np.nanmean(np.abs(x-y))
    
def RMSE(x,y):
    # from: https://en.wikipedia.org/wiki/Root-mean-square_deviation

    n = len(x)
    m = len(y)

    if np.sum(np.isnan(x)) == n or np.sum(np.isnan(y)) == m: return np.NaN

    return np.sqrt(np.nanmean(np.square(x-y)))

def pearsonR(x,y):
    # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.stats.pearsonr.html

    n = len(x)
    m = len(y)

    if np.sum(np.isnan(x)) == n or np.sum(np.isnan(y)) == m: return np.NaN

    R,p = sps.pearsonr(x,y)
    return R