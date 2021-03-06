import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, classification_report
import matplotlib.pylab as plt
import datetime as dt
import time
from normalizer import *

def load_snp_returns():
    f = open('table.csv', 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            open_price = float(line.split(',')[1])
            close_price = float(line.split(',')[4])
            raw_data.append(close_price - open_price)
            raw_dates.append(line.split(',')[0])
        except:
            continue

    return raw_data[::-1], raw_dates[::-1]


def load_snp_close():
    f = open('table.csv', 'rb').readlines()[1:]
    raw_data = []
    raw_dates = []
    for line in f:
        try:
            close_price = float(line.split(',')[4])
            raw_data.append(close_price)
            raw_dates.append(line.split(',')[0])
        except:
            continue

    return raw_data, raw_dates


def split_into_chunks(data, train, predict, step, binary=True, scale=True):
    X, Y = [], []
    for i in range(0, len(data)-train-predict, step):
        try:
            x_i = data[i:i+train]
            y_i = data[i+train+predict]
            
            # Use it only for daily return time series
            if binary:
                if y_i > 0.:
                    y_i = [1., 0.]
                else:
                    y_i = [0., 1.]

                if scale: x_i = (np.array(x_i) - np.mean(x_i)) / np.std(x_i)
                
            else:
                timeseries = np.array(data[i:i+train+predict])
                if scale:
                    half_window = 11
                    timeseries = timeseries-timeseries[half_window]
                    y_i = timeseries[-1]
                    #y_i = (y_i - np.mean(timeseries[:-1])) / np.std(timeseries[:-1])
                    #x_i = (np.array(timeseries[:-1]) - np.mean(timeseries[:-1])) / np.std(timeseries[:-1])
                    x_i = timeseries[:-1]
                else:
                    x_i = timeseries[:-1]
                    y_i = timeseries[-1]
            
        except:
            break

        X.append(x_i)
        Y.append(y_i)

    return X, Y

def split_into_chunks_adaptive(data, ewm, train, predict, step, binary=True, scale=True):
    X, Y, shift = [], [], []
    for i in range(0, len(data)-train-predict, step):
        try:
            # Use it only for daily return time series
            if binary:
                x_i = data[i:i + train]
                y_i = data[i + train + predict]
                if y_i > 0.:
                    y_i = [1., 0.]
                else:
                    y_i = [0., 1.]

                if scale: x_i = (np.array(x_i) - np.mean(x_i)) / np.std(x_i)
                
            else:
                timeseries = np.array(data[i:i+train+predict])
                shift_i = np.array(ewm[i])
                #shift_i = np.mean(timeseries[:-1])

                if scale:
                    timeseries = timeseries-shift_i
                    y_i = timeseries[-1]
                    #y_i = (y_i - np.mean(timeseries[:-1])) / np.std(timeseries[:-1])
                    #x_i = (np.array(timeseries[:-1]) - np.mean(timeseries[:-1])) / np.std(timeseries[:-1])
                    x_i = timeseries[:-1]
                else:
                    x_i = timeseries[:-1]
                    y_i = timeseries[-1]
            
        except:
            break

        X.append(x_i)
        Y.append(y_i)
        shift.append(shift_i)

    return X, Y, shift


def split_into_chunks_adaptive_type(data, ewm, train, predict, step, binary=True, scale=True, type='o'):
    X, Y, shift = [], [], []
    for i in range(0, len(data) - train - predict, step):
        try:
            # Use it only for daily return time series
            if binary:
                x_i = data[i:i + train]
                y_i = data[i + train + predict]
                if y_i > 0.:
                    y_i = [1., 0.]
                else:
                    y_i = [0., 1.]

                if scale: x_i = (np.array(x_i) - np.mean(x_i)) / np.std(x_i)

            else:
                timeseries = np.array(data[i:i + train + predict])
                shift_i = np.array(ewm[i])
                # shift_i = np.mean(timeseries[:-1])

                if scale:
                    if (type == 'o'):
                        timeseries = timeseries / shift_i
                    elif (type == 'c'):
                        timeseries = (timeseries + 1) / (shift_i + 1)
                    elif (type == 'd'):
                        timeseries = timeseries - shift_i

                    y_i = timeseries[-1]
                    # y_i = (y_i - np.mean(timeseries[:-1])) / np.std(timeseries[:-1])
                    # x_i = (np.array(timeseries[:-1]) - np.mean(timeseries[:-1])) / np.std(timeseries[:-1])
                    x_i = timeseries[:-1]
                else:
                    x_i = timeseries[:-1]
                    y_i = timeseries[-1]

        except:
            break

        X.append(x_i)
        Y.append(y_i)
        shift.append(shift_i)

    return X, Y, shift

#
# def split_into_chunks_adaptive_try(data, ewm, train, predict, step):
#     X, Y, shift, R = [], [], [], []
#     data, ewm = np.array(data), np.array(ewm)
#     #generating new sequence R with adaptive normalization
#
#     for i in range(0, len(data)-train-predict, step):
#         try:
#             for j in range(1, len(data[i:i+train+predict]) + 1, 1):  #for not having 0 division, it has to start at 1, so add that 1 in the end
#                 R.append(data[i:i+train+predict][int(np.ceil(j / (train + predict)) * (j - 1) % (train + predict))]
#                          / ewm[i:i+train+predict][int(np.ceil(j / (train + predict)))])
#                 shift.append(ewm[i:i+train+predict][int(np.ceil(j / (train + predict)))])
#
#             timeseries = np.array(R[i:i + train + predict])
#             x_i = timeseries[:-1]
#             y_i = timeseries[-1]
#
#         except:
#             break
#
#         X.append(x_i)
#         Y.append(y_i)
#
#     return X, Y, shift, R



def shuffle_in_unison(a, b):
    # courtsey http://stackoverflow.com/users/190280/josh-bleecher-snyder
    assert len(a) == len(b)
    shuffled_a = np.empty(a.shape, dtype=a.dtype)
    shuffled_b = np.empty(b.shape, dtype=b.dtype)
    permutation = np.random.permutation(len(a))
    for old_index, new_index in enumerate(permutation):
        shuffled_a[new_index] = a[old_index]
        shuffled_b[new_index] = b[old_index]
    return shuffled_a, shuffled_b

def shuffle_in_unison_adaptive(a, b, c):
    # courtsey http://stackoverflow.com/users/190280/josh-bleecher-snyder
    assert len(a) == len(b)
    assert len(b) == len(c)
    shuffled_a = np.empty(a.shape, dtype=a.dtype)
    shuffled_b = np.empty(b.shape, dtype=b.dtype)
    shuffled_c = np.empty(c.shape, dtype=c.dtype)
    permutation = np.random.permutation(len(a))
    for old_index, new_index in enumerate(permutation):
        shuffled_a[new_index] = a[old_index]
        shuffled_b[new_index] = b[old_index]
        shuffled_c[new_index] = c[old_index]
    return shuffled_a, shuffled_b, shuffled_c

#
# def create_Train_Test(data, percentage=0.8):
#     Train = data[0:int(len(data) * percentage)]
#
#     Test = data[int(len(data) * percentage):]
#
#     return Train, Test


def create_Xt_Yt(X, y, percentage=0.8):
    X_train = X[0:int(len(X) * percentage)]
    Y_train = y[0:int(len(y) * percentage)]
    
    #X_train, Y_train = shuffle_in_unison(X_train, Y_train)

    X_test = X[int(len(X) * percentage):]
    Y_test = y[int(len(y) * percentage):]

    return X_train, X_test, Y_train, Y_test

def create_Xt_Yt_adaptive(X, y, shift, percentage=0.8):
    X_train = X[0:int(len(X) * percentage)]
    Y_train = y[0:int(len(y) * percentage)]
    shift_train = shift[0:int(len(shift) * percentage)]
    
    #X_train, Y_train, shift_train = shuffle_in_unison_adaptive(X_train, Y_train, shift_train)

    X_test = X[int(len(X) * percentage):]
    Y_test = y[int(len(y) * percentage):]
    shift_test = shift[int(len(shift) * percentage):]

    return X_train, X_test, Y_train, Y_test, shift_train, shift_test


from statsmodels.tsa.stattools import adfuller
#check if timeseries is stationary
def test_stationarity(timeseries):

    #Determing rolling statistics
    rolmean = timeseries.rolling(window=12,center=False).mean()
    rolstd = timeseries.rolling(window=12,center=False).std()

    #Plot rolling statistics:
    orig = plt.plot(timeseries, color='blue',label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    std = plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)

    #Perform Dickey-Fuller test:
    print('Results of Dickey-Fuller Test:')
    dftest = adfuller(timeseries.values, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    print(dfoutput)



#minmax normalization without sliding windows

def nn_mm(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE):
    X, Y = split_into_chunks(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
    X, Y = np.array(X), np.array(Y)
    X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, Y)

    X_train, Y_train = remove_outliers(X_train, Y_train)

    X_test, Y_test = remove_outliers(X_test, Y_test)

    X_trainp, Y_trainp, X_testp, Y_testp = X_train, Y_train, X_test, Y_test

    #saving original shapes
    X_train_shape = X_train.shape
    X_test_shape = X_test.shape
    Y_train_shape = Y_train.shape
    Y_test_shape = Y_test.shape

    X_train, scaler = minMaxNormalize(X_train.reshape(-1,1))
    X_train = X_train.reshape(X_train_shape)

    X_test = minMaxNormalizeOver(X_test.reshape(-1,1), scaler)
    X_test = X_test.reshape(X_test_shape)

    Y_train = minMaxNormalizeOver(Y_train.reshape(-1,1), scaler)
    Y_train = Y_train.reshape(Y_train_shape)

    Y_test = minMaxNormalizeOver(Y_test.reshape(-1,1), scaler)
    Y_test = Y_test.reshape(Y_test_shape)


    return X_train, X_test, Y_train, Y_test, scaler, X_trainp, X_testp, Y_trainp, Y_testp

def nn_mm_den(X_train, X_test, Y_train, Y_test, scaler):
    X_train_shape = X_train.shape
    X_test_shape = X_test.shape
    Y_train_shape = Y_train.shape
    Y_test_shape = Y_test.shape

    X_train = minMaxDenormalize(X_train.reshape(-1, 1), scaler)
    X_train = X_train.reshape(X_train_shape)

    X_test = minMaxDenormalize(X_test.reshape(-1, 1), scaler)
    X_test = X_test.reshape(X_test_shape)

    Y_train = minMaxDenormalize(Y_train.reshape(-1, 1), scaler)
    Y_train = Y_train.reshape(Y_train_shape)

    Y_test = minMaxDenormalize(Y_test.reshape(-1, 1), scaler)
    Y_test = Y_test.reshape(Y_test_shape)


    X_train, X_test, Y_train, Y_test = np.array(X_train), np.array(X_test), np.array(Y_train), np.array(Y_test)
    return X_train, X_test, Y_train, Y_test


#minmax normalization with sliding windows

def nn_sw(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE):

    X, Y = split_into_chunks(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
    X, Y = np.array(X), np.array(Y)
    X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, Y)

    if X_train.ndim > 2:
        train_shape = X_train.shape[-1]

    X_train, Y_train = remove_outliers(X_train, Y_train)
    X_test, Y_test = remove_outliers(X_test, Y_test)

    X_trainp, Y_trainp, X_testp, Y_testp = X_train, Y_train, X_test, Y_test

    X_train_n, X_test_n, Y_train_n, Y_test_n, scaler_train, scaler_test = [],[],[],[],[],[]
    for i in range(X_train.shape[0]):
        X_normalizado, scaler = minMaxNormalize(X_train[i].reshape(-1,1)) # shape(30,1)
        if X_train.ndim > 2:
            X_train_n.append(X_normalizado.reshape(-1, train_shape)) # shape(30)
        else:
            X_train_n.append(X_normalizado.reshape(-1))
        Y_train_n.append(minMaxNormalizeOver(Y_train[i].reshape(-1, 1), scaler).reshape(-1))
        scaler_train.append(scaler)

    for i in range(X_test.shape[0]):
        X_normalizado, scaler = minMaxNormalize(X_test[i].reshape(-1, 1))  # shape(30,1)
        if X_train.ndim > 2:
            X_test_n.append(X_normalizado.reshape(-1, train_shape))  # shape(30, shape)
        else:
            X_test_n.append(X_normalizado.reshape(-1))  # shape(30)
        Y_test_n.append(minMaxNormalizeOver(Y_test[i].reshape(-1, 1), scaler).reshape(-1))
        scaler_test.append(scaler)

    X_train, X_test, Y_train, Y_test = np.array(X_train_n), np.array(X_test_n), np.array(Y_train_n), np.array(Y_test_n)
    return X_train, X_test, Y_train, Y_test, scaler_train, scaler_test, X_trainp, X_testp, Y_trainp, Y_testp

def nn_sw_den(X_train, X_test, Y_train, Y_test, scaler_train, scaler_test):
    if X_train.ndim > 2:
        train_shape = X_train.shape[-1]

    X_train_d, X_test_d, Y_train_d, Y_test_d = [], [], [], []
    for i in range(X_train.shape[0]):
        if X_train.ndim > 2:
            X_denormalizado = minMaxDenormalize(X_train[i].reshape(-1, 1), scaler_train[i]).reshape(-1, train_shape)
        else:
            X_denormalizado = minMaxDenormalize(X_train[i].reshape(-1, 1), scaler_train[i]).reshape(-1)
        X_train_d.append(X_denormalizado)
        Y_denormalizado = minMaxDenormalize(Y_train[i].reshape(-1, 1), scaler_train[i]).reshape(-1)
        Y_train_d.append(Y_denormalizado)

    for i in range(X_test.shape[0]):
        if X_train.ndim > 2:
            X_denormalizado = minMaxDenormalize(X_test[i].reshape(-1, 1), scaler_test[i]).reshape(-1, train_shape)
        else:
            X_denormalizado = minMaxDenormalize(X_test[i].reshape(-1, 1), scaler_test[i]).reshape(-1)
        X_test_d.append(X_denormalizado)
        Y_denormalizado = minMaxDenormalize(Y_test[i].reshape(-1, 1), scaler_test[i]).reshape(-1)
        Y_test_d.append(Y_denormalizado)

    X_train, X_test, Y_train, Y_test = np.array(X_train_d), np.array(X_test_d), np.array(Y_train_d), np.array(Y_test_d)
    return X_train, X_test, Y_train, Y_test


#z-score normalization
def nn_zs(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE):
    X, Y = split_into_chunks(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
    X, Y = np.array(X), np.array(Y)
    X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, Y)

    X_train, Y_train = remove_outliers(X_train, Y_train)
    X_test, Y_test = remove_outliers(X_test, Y_test)

    X_trainp, Y_trainp, X_testp, Y_testp = X_train, Y_train, X_test, Y_test

    # saving original shapes
    X_train_shape = X_train.shape
    X_test_shape = X_test.shape
    Y_train_shape = Y_train.shape
    Y_test_shape = Y_test.shape

    X_train, scaler = zNormalize(X_train.reshape(-1, 1))
    X_train = X_train.reshape(X_train_shape)

    X_test = zNormalizeOver(X_test.reshape(-1, 1), scaler)
    X_test = X_test.reshape(X_test_shape)

    Y_train = zNormalizeOver(Y_train.reshape(-1, 1), scaler)
    Y_train = Y_train.reshape(Y_train_shape)

    Y_test = zNormalizeOver(Y_test.reshape(-1, 1), scaler)
    Y_test = Y_test.reshape(Y_test_shape)

    return X_train, X_test, Y_train, Y_test, scaler, X_trainp, X_testp, Y_trainp, Y_testp

def nn_zs_den(X_train, X_test, Y_train, Y_test, scaler):
    X_train = zDenormalize(X_train, scaler)
    X_test = zDenormalize(X_test, scaler)
    Y_train = zDenormalize(Y_train, scaler)
    Y_test = zDenormalize(Y_test, scaler)
    X_train, X_test, Y_train, Y_test = np.array(X_train), np.array(X_test), np.array(Y_train), np.array(Y_test)
    return X_train, X_test, Y_train, Y_test

#decimal normalization
def nn_ds(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE):
    X, Y = split_into_chunks(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
    X, Y = np.array(X), np.array(Y)
    X_train, X_test, Y_train, Y_test = create_Xt_Yt(X, Y)

    X_train, Y_train = remove_outliers(X_train, Y_train)
    X_test, Y_test = remove_outliers(X_test, Y_test)

    X_trainp, Y_trainp, X_testp, Y_testp = X_train, Y_train, X_test, Y_test

    maximum = max(X_train.reshape(-1))

    # saving original shapes
    X_train_shape = X_train.shape
    X_test_shape = X_test.shape
    Y_train_shape = Y_train.shape
    Y_test_shape = Y_test.shape

    X_train = decimalNormalize(X_train.reshape(-1, 1))
    X_train = X_train.reshape(X_train_shape)


    X_test = decimalNormalizeOver(X_test.reshape(-1, 1), maximum)
    X_test = X_test.reshape(X_test_shape)

    Y_train = decimalNormalizeOver(Y_train.reshape(-1, 1), maximum)
    Y_train = Y_train.reshape(Y_train_shape)

    Y_test = decimalNormalizeOver(Y_test.reshape(-1, 1), maximum)
    Y_test = Y_test.reshape(Y_test_shape)

    return X_train, X_test, Y_train, Y_test, maximum, X_trainp, X_testp, Y_trainp, Y_testp

def nn_ds_den(X_train, X_test, Y_train, Y_test, maximum):
    X_train = decimalDenormalize(X_train, maximum)
    X_test = decimalDenormalize(X_test, maximum)
    Y_train = decimalDenormalize(Y_train, maximum)
    Y_test = decimalDenormalize(Y_test, maximum)
    X_train, X_test, Y_train, Y_test = np.array(X_train), np.array(X_test), np.array(Y_train), np.array(Y_test)
    return X_train, X_test, Y_train, Y_test


#adaptive normalization (Adaptive Normalization: A Novel Data Normalization Approach for  Non-Stationary Time Series)
def nn_an(dataset, ewm, TRAIN_SIZE, TARGET_TIME, LAG_SIZE):
    X, Y = split_into_chunks(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
    X, Y = np.array(X), np.array(Y)
    X_trainp, X_testp, Y_trainp, Y_testp = create_Xt_Yt(X, Y) # keeping track of the original values

    X, Y, shift = split_into_chunks_adaptive(dataset, ewm, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False,
                                             scale=True)
    X, Y, shift = np.array(X), np.array(Y), np.array(shift)
    X_train, X_test, Y_train, Y_test, shift_train, shift_test = create_Xt_Yt_adaptive(X, Y, shift)
    X_train, Y_train, shift_train, X_trainp, Y_trainp = remove_outliers_adaptive(X_train,Y_train, shift_train, X_trainp, Y_trainp)

    X_test, Y_test, shift_test, X_testp, Y_testp = remove_outliers_adaptive(X_test, Y_test, shift_test, X_testp, Y_testp)

    if X_train.ndim > 2:
        train_shape = X_train.shape[-1]

    sample_normalizado, scaler = minMaxNormalize(X_train.reshape(-1,1))# global scaler over sample set, as said on the article
    X_train_n, X_test_n, Y_train_n, Y_test_n= [], [], [], []
    for i in range(X_train.shape[0]):
        X_normalizado = minMaxNormalizeOver(X_train[i].reshape(-1, 1), scaler)  # shape(30,1)
        if X_train.ndim > 2:
            X_train_n.append(X_normalizado.reshape(-1, train_shape))
        else:
            X_train_n.append(X_normalizado.reshape(-1))
        Y_train_n.append(minMaxNormalizeOver(Y_train[i].reshape(-1, 1), scaler).reshape(-1))

    for i in range(X_test.shape[0]):
        X_normalizado = minMaxNormalizeOver(X_test[i].reshape(-1, 1), scaler)  # shape(TRAIN_SIZE*shape,1)
        if X_train.ndim > 2:
            X_test_n.append(X_normalizado.reshape(-1, train_shape))  # shape(TRAIN_SIZE, shape)
        else:
            X_test_n.append(X_normalizado.reshape(-1))  # shape(TRAIN_SIZE, )
        Y_test_n.append(minMaxNormalizeOver(Y_test[i].reshape(-1, 1), scaler).reshape(-1))

    X_train, X_test, Y_train, Y_test = np.array(X_train_n), np.array(X_test_n), np.array(Y_train_n), np.array(Y_test_n)
    return X_train, X_test, Y_train, Y_test, scaler, shift_train, shift_test, X_trainp, X_testp, Y_trainp, Y_testp

def nn_an_type(dataset, ewm, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, type):
    X, Y = split_into_chunks(dataset, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False, scale=False)
    X, Y = np.array(X), np.array(Y)
    X_trainp, X_testp, Y_trainp, Y_testp = create_Xt_Yt(X, Y) # keeping track of the original values

    X, Y, shift = split_into_chunks_adaptive_type(dataset, ewm, TRAIN_SIZE, TARGET_TIME, LAG_SIZE, binary=False,
                                             scale=True, type=type)
    X, Y, shift = np.array(X), np.array(Y), np.array(shift)
    X_train, X_test, Y_train, Y_test, shift_train, shift_test = create_Xt_Yt_adaptive(X, Y, shift)
    X_train, Y_train, shift_train, X_trainp, Y_trainp = remove_outliers_adaptive(X_train,Y_train, shift_train, X_trainp, Y_trainp)

    X_test, Y_test, shift_test, X_testp, Y_testp = remove_outliers_adaptive(X_test, Y_test, shift_test, X_testp, Y_testp)

    if X_train.ndim > 2:
        train_shape = X_train.shape[-1]

    sample_normalizado, scaler = minMaxNormalize(X_train.reshape(-1,1))# global scaler over sample set, as said on the article
    X_train_n, X_test_n, Y_train_n, Y_test_n= [], [], [], []
    for i in range(X_train.shape[0]):
        X_normalizado = minMaxNormalizeOver(X_train[i].reshape(-1, 1), scaler)  # shape(30,1)
        if X_train.ndim > 2:
            X_train_n.append(X_normalizado.reshape(-1, train_shape))
        else:
            X_train_n.append(X_normalizado.reshape(-1))
        Y_train_n.append(minMaxNormalizeOver(Y_train[i].reshape(-1, 1), scaler).reshape(-1))

    for i in range(X_test.shape[0]):
        X_normalizado = minMaxNormalizeOver(X_test[i].reshape(-1, 1), scaler)  # shape(TRAIN_SIZE*shape,1)
        if X_train.ndim > 2:
            X_test_n.append(X_normalizado.reshape(-1, train_shape))  # shape(TRAIN_SIZE, shape)
        else:
            X_test_n.append(X_normalizado.reshape(-1))  # shape(TRAIN_SIZE, )
        Y_test_n.append(minMaxNormalizeOver(Y_test[i].reshape(-1, 1), scaler).reshape(-1))

    X_train, X_test, Y_train, Y_test = np.array(X_train_n), np.array(X_test_n), np.array(Y_train_n), np.array(Y_test_n)
    return X_train, X_test, Y_train, Y_test, scaler, shift_train, shift_test, X_trainp, X_testp, Y_trainp, Y_testp


def nn_an_den(X_train, X_test, Y_train, Y_test, scaler, shift_train, shift_test):
    if X_train.ndim > 2:
        train_shape = X_train.shape[-1]

    X_train_d, X_test_d, Y_train_d, Y_test_d = [], [], [], []
    for i in range(X_train.shape[0]):
        if X_train.ndim > 2:
            X_denormalizado = minMaxDenormalize(X_train[i].reshape(-1, 1), scaler).reshape(-1, train_shape)
        else:
            X_denormalizado = minMaxDenormalize(X_train[i].reshape(-1, 1), scaler).reshape(-1)
        X_denormalizado = X_denormalizado + shift_train[i]
        X_train_d.append(X_denormalizado)
        Y_denormalizado = minMaxDenormalize(Y_train[i].reshape(-1, 1), scaler).reshape(-1)
        Y_denormalizado = Y_denormalizado + shift_train[i]
        Y_train_d.append(Y_denormalizado)

    for i in range(X_test.shape[0]):
        if X_train.ndim > 2:
            X_denormalizado = minMaxDenormalize(X_test[i].reshape(-1, 1), scaler).reshape(-1, train_shape)
        else:
            X_denormalizado = minMaxDenormalize(X_test[i].reshape(-1, 1), scaler).reshape(-1)
        X_denormalizado = X_denormalizado + shift_test[i]
        X_test_d.append(X_denormalizado)
        Y_denormalizado = minMaxDenormalize(Y_test[i].reshape(-1, 1), scaler).reshape(-1)
        Y_denormalizado = Y_denormalizado + shift_test[i]
        Y_test_d.append(Y_denormalizado)

    X_train, X_test, Y_train, Y_test = np.array(X_train_d), np.array(X_test_d), np.array(Y_train_d), np.array(Y_test_d)
    return X_train, X_test, Y_train, Y_test

def nn_an_den_type(X_train, X_test, Y_train, Y_test, scaler, shift_train, shift_test, type):
    if X_train.ndim > 2:
        train_shape = X_train.shape[-1]

    X_train_d, X_test_d, Y_train_d, Y_test_d = [], [], [], []
    for i in range(X_train.shape[0]):
        if X_train.ndim > 2:
            X_denormalizado = minMaxDenormalize(X_train[i].reshape(-1, 1), scaler).reshape(-1, train_shape)
        else:
            X_denormalizado = minMaxDenormalize(X_train[i].reshape(-1, 1), scaler).reshape(-1)
        if(type == 'o'):
            X_denormalizado = X_denormalizado * shift_train[i]
        elif(type == 'c'):
            X_denormalizado = (X_denormalizado) * (shift_train[i])
        elif(type == 'd'):
            X_denormalizado = X_denormalizado + shift_train[i]

        X_train_d.append(X_denormalizado)
        Y_denormalizado = minMaxDenormalize(Y_train[i].reshape(-1, 1), scaler).reshape(-1)

        if(type == 'o'):
            Y_denormalizado = Y_denormalizado * shift_train[i]
        elif(type == 'c'):
            Y_denormalizado = (Y_denormalizado) * (shift_train[i])
        elif(type == 'd'):
            Y_denormalizado = Y_denormalizado + shift_train[i]

        Y_train_d.append(Y_denormalizado)

    for i in range(X_test.shape[0]):
        if X_train.ndim > 2:
            X_denormalizado = minMaxDenormalize(X_test[i].reshape(-1, 1), scaler).reshape(-1, train_shape)
        else:
            X_denormalizado = minMaxDenormalize(X_test[i].reshape(-1, 1), scaler).reshape(-1)
        X_denormalizado = X_denormalizado + shift_test[i]
        X_test_d.append(X_denormalizado)
        Y_denormalizado = minMaxDenormalize(Y_test[i].reshape(-1, 1), scaler).reshape(-1)
        Y_denormalizado = Y_denormalizado + shift_test[i]
        Y_test_d.append(Y_denormalizado)

    X_train, X_test, Y_train, Y_test = np.array(X_train_d), np.array(X_test_d), np.array(Y_train_d), np.array(Y_test_d)
    return X_train, X_test, Y_train, Y_test

def remove_outliers(X_train, Y_train, alpha = 1.5):
    q3 = np.percentile(X_train, 75)
    q1 = np.percentile(X_train, 25)
    IQR = q3 - q1
    lq1 = q1 - alpha*IQR
    hq3 = q3 + alpha*IQR
    new_X_train = []
    new_Y_train = []

    for i in range(len(X_train)):
        cond = (X_train[i] >= lq1) & (X_train[i] <= hq3)
        if (cond.all()):
            new_X_train.append(X_train[i])
            new_Y_train.append(Y_train[i])



    return np.array(new_X_train), np.array(new_Y_train)


def remove_outliers_adaptive(X_train, Y_train, shift_train, X_trainp, Y_trainp, alpha = 1.5):
    q3 = np.percentile(X_train, 75)
    q1 = np.percentile(X_train, 25)
    IQR = q3 - q1
    lq1 = q1 - alpha*IQR
    hq3 = q3 + alpha*IQR
    new_X_train = []
    new_Y_train = []
    new_shift_train = []
    new_X_trainp = []
    new_Y_trainp = []

    for i in range(len(X_train)):
        cond = (X_train[i] >= lq1) & (X_train[i] <= hq3)
        if (cond.all()):
            new_X_train.append(X_train[i])
            new_Y_train.append(Y_train[i])
            new_shift_train.append(shift_train[i])
            new_X_trainp.append(X_trainp[i])
            new_Y_trainp.append(Y_trainp[i])

    return np.array(new_X_train), np.array(new_Y_train), np.array(new_shift_train), np.array(new_X_trainp), np.array(new_Y_trainp)


# ts.outliers.boxplot <- function(data, alpha = 1.5)
# {
#   org = nrow(data)
#   q = as.data.frame(lapply(data, quantile))
#   n = ncol(data)
#   for (i in 1:n)
#   {
#     IQR = q[4,i] - q[2,i]
#     lq1 = q[2,i] - alpha*IQR
#     hq3 = q[4,i] + alpha*IQR
#     cond = data[,i] >= lq1 & data[,i] <= hq3
#     data = data[cond,]
#   }
#   final = nrow(data)
#   return (data)
# }
