import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat

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
        elif fileType in ['nidaq', 'running', 'eye', 'cam']:
            pathFile = "/{}-{}-00{}-{}.mat".format(self.mouse, self.date, self.run, fileType)
            return os.path.join(self.baseDir + pathDir + pathFile)
        else:
            raise NameError ('Unknown file type. Available data types: bhv, nidaq, running, eye, cam.')

    def setPath(self):
        self.path['bhv'] = self.filePath('bhv')
        self.path['nidaq'] = self.filePath('nidaq')
        self.path['running'] = self.filePath('running')
        self.path['eye'] = self.filePath('eye')
        self.path['cam'] = self.filePath('cam')

    def getPath(self):
        if len(self.path) == 0:
            raise IOError ('File paths are not defined.')
        else:
            return self.path

    def loadData(self, fileType= 'all'):
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

                print(txtcol.OKBLACK + 'Loading data for ' + self.mouse + ', run ' + str(self.run) + ' of ' + self.date + '...' + txtcol.END)
                if fileType in ['bhv', 'all']:
                    filePath = self.path['bhv']
                    if os.path.exists(filePath):
                        temp_bhv[self.run] = loadmat(filePath, squeeze_me= True)
                        print(txtcol.OKGREEN + 'MonkeyLogic data loaded.' + txtcol.END)
                    else:
                        temp_bhv[self.run] = pd.DataFrame([])
                        print(txtcol.FAIL + 'Data not found: MonkeyLogic' + txtcol.END)

                if fileType in ['nidaq', 'all']:
                    filePath = self.path['nidaq']
                    if os.path.exists(filePath):
                        temp_nidaq[self.run] = loadmat(filePath, squeeze_me= True)
                        print(txtcol.OKGREEN + 'NI-DAQ data loaded.' + txtcol.END)
                    else:
                        temp_nidaq[self.run] = pd.DataFrame([])
                        print(txtcol.FAIL + 'Data not found: NI-DAQ' + txtcol.END)

                if fileType in ['running', 'all']:
                    filePath = self.path['running']
                    if os.path.exists(filePath):
                        temp_running[self.run] = loadmat(filePath, squeeze_me= True)
                        print(txtcol.OKGREEN + 'Running data loaded.' + txtcol.END)
                    else:
                        temp_running[self.run] = pd.DataFrame([])
                        print(txtcol.FAIL + 'Data not found: running' + txtcol.END)

            self.data['bhv'][self.date] = temp_bhv
            self.data['nidaq'][self.date] = temp_nidaq
            self.data['running'][self.date] = temp_running
            print('- - -\n')

    def getTrials(self, save= False):
        self.bhv = {}
        self.codes = {  1 : 'Pavlovian_CSp_2s',
                            2 : 'CSmix_cond_2s_end',
                            3 : 'Pavlovian_CSm_shock',
                            4 : 'Blank_2s',
                            5 : 'Lick_reward',
                            6 : 'Unconditional_reward'}

        for date in self.dates:
            temp_bhv = {}
            for run in self.runs:
                df_bhv = pd.DataFrame([])
                self.setRun(date, run)
                if len(self.data['bhv'][self.date][self.run]) != 0:
                    print('yooo')
                    df_bhv['conditions'] = self.data['bhv'][self.date][self.run]['bhv']['conditions'].tolist()
                    df_bhv['trialerrors'] = self.data['bhv'][self.date][self.run]['bhv']['trialerrors'].tolist()
                    df_bhv['blocknum'] = self.data['bhv'][self.date][self.run]['bhv']['blocknumber'].tolist()
                    df_bhv['trialnum'] = np.arange(1, len(df_bhv['conditions']) + 1)
                    df_bhv['mouse'] = self.mouse
                    df_bhv['date'] = self.date
                    df_bhv['run'] = self.run
                    temp_bhv[self.run] = df_bhv

                self.bhv[self.date] = temp_bhv

if __name__ == '__main__':
    mouse = 'LR8'
    dates = ['180801', '180713']
    runs = [1, 2, 3]

    LR8 = behavior(mouse, dates, runs)
    LR8.setDir('/Volumes/User Folders/Trent/MixedValenceBehavior')
    LR8.loadData('all')
    LR8.getTrials()
