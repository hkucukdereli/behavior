import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat
import pickle

class txtcol:
    OKGREEN = '\033[92m'
    OKBLACK = '\033[0m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'

class behavior(txtcol):
    def __init__(self, mouse, dates, runs):
        self.mouse = mouse
        self.dates = dates
        self.runs = runs
        self.path = {}
        self.data = {}

    def getInfo(self):
        return {'Mouse' : self.mouse, 'Dates' : self.dates, 'Runs' : self.runs}

    def setDir(self, baseDir):
        self.baseDir = baseDir
        if os.path.isdir(baseDir):
            print('Base directory is set to ' + self.baseDir + '\n')
        else:
            raise IOError('Directory not found!')

    def setRun(self, date, run):
        self.date = date
        self.run = run

    def filePath(self, fileType):
        pathDir = "/{}/{}_{}/{}_{}_Run{}".format(self.mouse, self.date, self.mouse, self.date, self.mouse, self.run)

        if fileType == 'bhv':
            pathFile = "/{}_{}_Run{}-{}.mat".format(self.date, self.mouse, self.run, 'bhv')
            return os.path.join(self.baseDir + pathDir + pathFile)
        elif fileType == 'bhv_':
            pathFile = "/Experiment-{}-{}-{}-20{}-bhv.mat".format(self.mouse, self.date[2:4], self.date[4:6], self.date[0:2])
            return os.path.join(self.baseDir + pathDir + pathFile)
        elif fileType in ['nidaq', 'running', 'eye', 'cam']:
            pathFile = "/{}-{}-00{}-{}.mat".format(self.mouse, self.date, self.run, fileType)
            return os.path.join(self.baseDir + pathDir + pathFile)
        else:
            raise NameError ('Unknown file type. Available data types: bhv, nidaq, running, eye, cam.')

    def setPath(self):
        if os.path.exists(self.filePath('bhv')):
            self.path['bhv'] = self.filePath('bhv')
        else:
            self.path['bhv'] = self.filePath('bhv_')
        self.path['nidaq'] = self.filePath('nidaq')
        self.path['running'] = self.filePath('running')
        self.path['eye'] = self.filePath('eye')
        self.path['cam'] = self.filePath('cam')

    def getPath(self):
        if len(self.path) == 0:
            raise IOError ('File paths are not defined.')
        else:
            return self.path

    def loadData(self, fileType= 'all', verbose= True, save= False):
        self.data['bhv'] = {}
        self.data['nidaq'] = {}
        self.data['running'] = {}

        for date in self.dates:
            temp_bhv = {}
            temp_nidaq = {}
            temp_running = {}
            for run in self.runs:
                self.setRun(date, run)
                self.setPath()

                if verbose:
                    print(txtcol.OKBLACK + 'Loading data for ' + self.mouse + ', run ' + str(self.run) + ' of ' + self.date + '...' + txtcol.END)
                if fileType in ['bhv', 'all']:
                    filePath = self.path['bhv']
                    if os.path.exists(filePath):
                        temp_bhv[self.run] = loadmat(filePath, squeeze_me= True)
                        if verbose:
                            print(txtcol.OKGREEN + 'MonkeyLogic data loaded.' + txtcol.END)
                    else:
                        temp_bhv[self.run] = pd.DataFrame([])
                        if verbose:
                            print(txtcol.FAIL + 'Data not found: MonkeyLogic' + txtcol.END)

                if fileType in ['nidaq', 'all']:
                    filePath = self.path['nidaq']
                    if os.path.exists(filePath):
                        temp_nidaq[self.run] = loadmat(filePath, squeeze_me= True)
                        if verbose:
                            print(txtcol.OKGREEN + 'NI-DAQ data loaded.' + txtcol.END)
                    else:
                        temp_nidaq[self.run] = pd.DataFrame([])
                        if verbose:
                            print(txtcol.FAIL + 'Data not found: NI-DAQ' + txtcol.END)

                if fileType in ['running', 'all']:
                    filePath = self.path['running']
                    if os.path.exists(filePath):
                        temp_running[self.run] = loadmat(filePath, squeeze_me= True)
                        if verbose:
                            print(txtcol.OKGREEN + 'Running data loaded.' + txtcol.END)
                    else:
                        temp_running[self.run] = pd.DataFrame([])
                        if verbose:
                            print(txtcol.FAIL + 'Data not found: running' + txtcol.END)

            self.data['bhv'][self.date] = temp_bhv
            self.data['nidaq'][self.date] = temp_nidaq
            self.data['running'][self.date] = temp_running
            if verbose:
                print('- - -\n')

        if save:
            print('Saving locally...')
            with open('/Users/Amelia/Documents/hakan/data/CNO_trials/' + self.mouse + '.obj', 'wb') as handle:
                pickle.dump(self.data, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print('Saved.')

    def loadTrials(self, save= False):
        self.bhv = {}
        self.codes = {}

        for date in self.dates:
            temp_bhv = {}
            temp_codes = {}
            for run in self.runs:
                df_bhv = pd.DataFrame([])
                self.setRun(date, run)
                if len(self.data['bhv'][self.date][self.run]) != 0:
                    df_bhv['conditions'] = self.data['bhv'][self.date][self.run]['bhv']['conditions'].tolist()
                    df_bhv['trialerrors'] = self.data['bhv'][self.date][self.run]['bhv']['trialerrors'].tolist()
                    df_bhv['blocknum'] = self.data['bhv'][self.date][self.run]['bhv']['blocknumber'].tolist()
                    df_bhv['trialnum'] = np.arange(1, len(df_bhv['conditions']) + 1)
                    df_bhv['mouse'] = self.mouse
                    df_bhv['date'] = self.date
                    df_bhv['run'] = self.run
                    temp_bhv[self.run] = df_bhv
                    temp_codes[self.run] = {1 : 'Pavlovian_CSp_2s',
                                            2 : 'CSmix_cond_2s_end',
                                            3 : 'Pavlovian_CSm_shock',
                                            4 : 'Blank_2s',
                                            5 : 'Lick_reward',
                                            6 : 'Unconditional_reward'}

                self.bhv[self.date] = temp_bhv
                self.codes[self.date] = temp_codes

            if save:
                print('Saving locally...')
                with open('/Users/Amelia/Documents/hakan/data/CNO_trials/' + self.mouse + '_bhv.obj', 'wb') as handle:
                    pickle.dump(self.bhv, handle, protocol=pickle.HIGHEST_PROTOCOL)
                with open('/Users/Amelia/Documents/hakan/data/CNO_trials/' + self.mouse + '_codes.obj', 'wb') as handle:
                    pickle.dump(self.codes, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print('Saved.')

    def loadNidaq(self, clean= True, save= False):
        self.nidaq = {}

        for date in self.dates:
            tempRun = {}
            for run in self.runs:
                self.setRun(date, run)
                NIDAQ = self.data['nidaq'][self.date][self.run]
                RUNNING = self.data['running'][self.date][self.run]

                self.channels = pd.DataFrame(NIDAQ['channelnames'].reshape(6,2), columns= ['ch_name', 'ch_num'])
                ch_names = self.channels['ch_name'].values

                temp = pd.DataFrame(NIDAQ['data'][0:len(ch_names)].transpose(), columns= ch_names)
                if clean:
                    temp[temp > 0.5] = 5.0
                    temp[temp <= 0.5] = 0.0
                    temp.iloc[-1] = 0.0
                temp['timestamps'] = NIDAQ['timestamps'].round(4)
                temp['mouse'] = self.mouse
                temp['date'] = self.date
                temp['run'] = self.run
                #self.nidaq.Fs = self.data[self.run]['Fs']

                tempRun[self.run] = temp

            self.nidaq[self.date] = tempRun

        if save:
            print('Saving locally...')
            with open('/Users/Amelia/Documents/hakan/data/CNO_trials/' + self.mouse + '_nidaq.obj', 'wb') as handle:
                pickle.dump(self.nidaq, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print('Saved.')

    def loadRunning(self, save= False):
        self.running = {}

        for date in self.dates:
            temp = {}
            for run in self.runs:
                self.setRun(date, run)

                speed = self.data['running'][self.date][self.run]['speed']
                position = self.data['running'][self.date][self.run]['position']
                temp[self.run] = pd.DataFrame({'speed' : speed, 'position' : position})
                temp[self.run]['mouse'] = self.mouse
                temp[self.run]['date'] = self.date
                temp[self.run]['run'] = self.run
                if len(self.nidaq[self.date][self.run]) > 0:
                    duration = self.nidaq[self.date][self.run]['timestamps'].iloc[-1]
                    temp[self.run]['timestamps'] = np.linspace(0.0, duration, len(speed))

            self.running[self.date] = temp

        if save:
            print('Saving locally...')
            with open('/Users/Amelia/Documents/hakan/data/CNO_trials/' + self.mouse + '_running.obj', 'wb') as handle:
                pickle.dump(self.running, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print('Saved.')

    def getData(self, fileType, date, run):
        if fileType in ['bhv', 'nidaq', 'running', 'eye', 'cam']:
            if len(self.data[fileType][date][run]) != 0:
                return self.data[fileType][date][run]
            else:
                raise IOError (fileType + ' data is not loaded.')
        else:
            raise NameError ('Unknown file type. Available data types: bhv, nidaq, running, eye, cam.')

    def getPerformance(self, date, run):
        if len(self.data['bhv'][date][run]) != 0:
            performance = pd.DataFrame({'conditions' : self.codes[date][run]})
            # performance['hit'] = np.empty(len(performance))
            # performance['miss'] = np.empty(len(performance))
            hits = []
            misses = []
            for con in self.codes[date][run]:
                temp = self.bhv[date][run][self.bhv[date][run]['conditions'] == con]
                if len(temp['trialerrors']) > 0:
                    hit = len(temp['trialerrors'][temp['trialerrors'] == min(set(temp['trialerrors']))]) * 1.0 / len(temp['trialerrors'])
                    miss = len(temp['trialerrors'][temp['trialerrors'] == max(set(temp['trialerrors']))]) * 1.0 / len(temp['trialerrors'])
                    # performance['hit'].loc[con] = hit
                    # performance['miss'].loc[con] = miss
                else:
                    hit = 0.0
                    miss = 0.0
                    # performance['hit'].loc[con] = 0.0
                    # performance['miss'].loc[con] = 0.0
                hits.append(hit)
                misses.append(miss)
            performance['hit'] = hits
            performance['miss'] = misses

            return performance
        else:
            raise IOError ('bhv' + ' data is not loaded.')

    def getFs(self):
        return self.data['nidaq'][self.date][self.run]['frequency']

if __name__ == '__main__':
    mouse = 'LR8'
    dates = ['180801']
    runs = [1]

    LR8 = behavior(mouse, dates, runs)
    LR8.setDir('/Volumes/User Folders/Trent/MixedValenceBehavior')
    LR8.loadData('all')
    LR8.loadTrials()

    date = '180801'
    run = 1
    LR8.getPerformance(date, run)
