import os
import math
import numpy as np
import pandas as pd
import scipy.io as scio

def calldir(basedir, mouse, date, run):
    dirpath = basedir + '/{}/{}_{}'.format(mouse, date, mouse)
    if dirpath + '/{}_{}_run{}'.format(date, mouse, run) in os.listdir(dirpath):
        dirpath = dirpath + '/{}_{}_run{}'.format(date, mouse, run)
    else:
        dirpath = dirpath + '/{}_{}_Run{}'.format(date, mouse, run)

    return dirpath

def callpath(basedir, mouse, date, run, filetype):
    if filetype in ['bhv', 'nidaq', 'running']:
        if filetype in ['nidaq', 'running']:
            filetype = '-' + filetype + '.mat'
            path = calldir(basedir, mouse, date, run) + '/{}-{}-00{}{}'.format(mouse, date, run, filetype)
        else:
            filetype = '-' + filetype + '.mat'
            fname = '{}_{}_Run{}{}'.format(date, mouse, run, filetype)
            if fname in os.listdir(calldir(basedir, mouse, date, run)):
                path = calldir(basedir, mouse, date, run) + '/' + fname
            else:
                fname = '{}_{}_run{}{}'.format(date, mouse, run, filetype)
                if fname in os.listdir(calldir(basedir, mouse, date, run)):
                    path = path = calldir(basedir, mouse, date, run) + '/' + fname
                else:
                    path = calldir(basedir, mouse, date, run) + '/Experiment-{}-{}-{}-20{}-Run{}{}'.format(mouse, date[2:4], date[4:6], date[0:2], run, filetype)
    else:
        filetype = '.' + filetype
        fname = '{}_{}_Run{}{}'.format(date, mouse, run, filetype)
        if fname in os.listdir(calldir(basedir, mouse, date, run)):
            path = calldir(basedir, mouse, date, run) + '/' + fname
        else:
            path = calldir(basedir, mouse, date, run) + '/{}_{}_run{}{}'.format(date, mouse, run, filetype)

    return path

def loadBhv(mouse, date, run, basedir):
    path = callpath(basedir, mouse, date, run, 'bhv')
    bhv = scio.loadmat(path, squeeze_me=False)
    trialerror = pd.DataFrame(bhv['BHV']['TrialError'][0][0].reshape(len(bhv['BHV']['TrialError'][0][0])), columns=['TrialError'])

    return bhv, trialerror

def loadData(mouse, date, run, basedir, rig):
    if rig  in ['lbr', 'leftbottomrig', 'nn', 'noname']:
        path = callpath(basedir, mouse, date, run, 'txt')
        rawdata = pd.read_csv(path, sep=' ', header=None, names=['timestamp', 'event', 'value'], skip_blank_lines= True, error_bad_lines=False, engine='python')

        position = rawdata[rawdata['event'] == 'P'].reset_index(drop=True)
        running = resample(position)
        licks = rawdata[rawdata['event'] == 'L'].reset_index(drop=True)
        visstim = rawdata[rawdata['event'] == 'V'].reset_index(drop=True)
        shocks = rawdata[rawdata['event'] == 'S'].reset_index(drop=True)
        rewards = rawdata[rawdata['event'] == 'R'].reset_index(drop=True)

        return running, licks, visstim, shocks, rewards

    elif rig == 'ephys':
        path = callpath(basedir, mouse, date, run, 'running')
        runningdata = scio.loadmat(path, squeeze_me=False)
        running = pd.DataFrame([], columns= ['position', 'speed', 'timestamp'])
        running['position'] = runningdata['position'][0]
        running['speed'] = runningdata['speed'][0]
        running['timestamp'] = np.linspace(0, 1000/15., len(runningdata['speed'][0]))

        path = callpath(basedir, mouse, date, run, 'nidaq')
        data = scio.loadmat(path, squeeze_me=False)

        ons = {}
        for i in np.arange(0, len(data['data'])):
            data['data'][i][data['data'][i] >= 2] = 5
            data['data'][i][data['data'][i] < 2] = 0
            ev = np.diff(data['data'][i])
            ev = np.append(np.array([0]), ev)
            ons[i] = data['timestamps'][0][ev != 0]

        licks = ons[1]
        visstim = ons[3]
        shocks = ons[4]
        rewards = ons[5]

        return running, licks, visstim, shocks, rewards

    else:
        raise NameError('"' + str(rig) + '" is not a valid rig name.')
