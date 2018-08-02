import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat, savemat

class behIO:
    """
    Class for figuring file paths and loading mat files.
    """

    def __init__(self, mouse, date, runs):
        """
        Basic info about the experiment.
        Parameters
        ----------
        mouse: string
            Mouse run.
        date: string
            Experiment date.
        runs: list
            List of the runs to analyze.
        """
        self.mouse = mouse
        self.date = date
        self.runs = runs

    def setDir(self, baseDir):
        """
        Set the base directory to look for files.
        """
        self.baseDir = baseDir
        if os.path.isdir(baseDir):
            print('Base directory is set to ' + self.baseDir)
        else:
            raise IOError('Directory not found!')

    def getPath(self, fileType, run):
        """
        Get the file path for a target run and file type.
        Parameters
        ----------
        targetRun: int
            Which run to analyze.
        fileType: string
            File type options: nidaq, running, licking, ml
        """
        pathDir = "/{}/{}_{}/{}_{}_Run{}".format(self.mouse, self.date, self.mouse, self.date, self.mouse, run)
        if fileType == 'bhv':
            pathFile = "/{}_{}_Run{}-{}.mat".format(self.date, self.mouse, run, 'bhv')
            self.path = os.path.join(self.baseDir + pathDir + pathFile)
        else:
            pathFile = "/{}-{}-00{}-{}.mat".format(self.mouse, self.date, run, fileType)
            self.path = os.path.join(self.baseDir + pathDir + pathFile)

    def savePath(self, type, format):
        pathDir = "/{}/{}_{}/Figures".format(self.mouse, self.date, self.mouse, self.date, self.mouse)
        pathFile = "/{}-{}-Run{}-{}.{}".format(self.mouse, self.date, self.run, type, format)
        if not os.path.exists(os.path.join(self.baseDir + pathDir)):
            os.makedirs(os.path.join(self.baseDir + pathDir))
        self.pathSave = os.path.join(self.baseDir + pathDir + pathFile)
        return self.pathSave

    def loadRuns(self, fileType, targetRuns= 0):
        """
        Load the data from multiple runs.
        Parameters:
        -----------
        targetRuns: list of integers
            List of runs to load. Loads all if none defined.
        fileType: string
            File type options: nidaq, running, licking, ml
        Returns:
        --------
        data: dictionary of dictionaries
        """
        self.data = {}
        self.fileType = fileType
        if targetRuns:
            print('Runs ' + str(targetRuns) + ' will be loaded.')
            for run in targetRuns:
                self.getPath(self.fileType, run)
                self.data[run] = loadmat(self.path, squeeze_me= True)
            print('Finished loading run(s).\n')
        else:
            print('All runs will be loaded.')
            for run in self.runs:
                self.getPath(fileType, run)
                self.data[run] = loadmat(self.path, squeeze_me= True)
            print('Finished loading run(s).\n')

    def loadBHV(self, targetRuns= 0):
        self.rawBHV = {}
        if targetRuns:
            print('Runs ' + str(targetRuns) + ' will be loaded.')
            for run in targetRuns:
                self.getPath('bhv', run)
                self.rawBHV[run] = loadmat(self.path, squeeze_me= True)
            print('Finished loading ML data.')
        else:
            print('All runs will be loaded.')
            for run in self.runs:
                self.getPath('bhv', run)
                self.rawBHV[run] = loadmat(self.path, squeeze_me= True)
            print('Finished loading ML data.\n')

    def setRun(self, run):
        self.run = run

    def getTrials(self, save= False):
        """
        Load the trial info such as the trial number and the ml codes for each trial.
        """
        self.bhv = pd.DataFrame([])
        self.bhv['conditions'] = self.rawBHV[self.run]['bhv']['conditions'].tolist()
        self.bhv['trialerrors'] = self.rawBHV[self.run]['bhv']['trialerrors'].tolist()
        self.bhv['blocknum'] = self.rawBHV[self.run]['bhv']['blocknumber'].tolist()
        self.bhv['trialnum'] = np.arange(1, len(self.bhv['conditions'])+1)
        self.bhv['mouse'] = self.mouse
        self.bhv['date'] = self.date
        self.bhv['run'] = self.run
        self.bhv.codes = {  1 : 'Pavlovian_CSp_2s',
                            2 : 'CSmix_cond_2s_end',
                            3 : 'Pavlovian_CSm_shock',
                            4 : 'Blank_2s',
                            5 : 'Lick_reward',
                            6 : 'Unconditional_reward'}

    def getNidaq(self, clean= True, save= False):
        """
        Load the nidaq data & time stamps and organize them according to the channel names.
        """
        self.channels = pd.DataFrame(self.data[self.run]['channelnames'].reshape(6,2), columns= ['ch_name', 'ch_num'])
        ch_names = self.channels['ch_name'].values

        self.nidaq = pd.DataFrame(self.data[self.run]['data'][0:len(ch_names)].transpose(), columns= ch_names)
        self.nidaq['timestamps'] = self.data[self.run]['timestamps'].round(4)
        self.nidaq['mouse'] = self.mouse
        self.nidaq['date'] = self.date
        self.nidaq['run'] = self.run
        self.nidaq.Fs = self.data[self.run]['Fs']

        if clean:
            self.pulses = self.channels['ch_name'].values
            # Threshold the nidaq channels first
            for pulse in self.pulses:
                self.nidaq[pulse].loc[self.nidaq[pulse] > 0.5] = 5.0
                self.nidaq[pulse].loc[self.nidaq[pulse] <= 0.5] = 0.0

                if self.nidaq[pulse].loc[len(self.nidaq[pulse])-1] > 0.5:
                    self.nidaq[pulse].loc[len(self.nidaq[pulse])-1] = 0.0
                    self.nidaq[pulse].loc[len(self.nidaq[pulse])-2] = 0.0

        if save:
            savemat(self.path[:-4] + '_data.mat')

    def getFs(self):
        self.nidaq.Fs = self.data[self.run]['Fs']
        return self.nidaq.Fs

    def findOnsets(self, threshold= 2.0, save= False):
        """
        Find the event onsets and offsets.
        Parameters:
        -----------
        threshold: float
            Pulse detection threshold.
        Returns:
        --------
        pulseOnsets: dictionary
            Dictionary of pulse onsets and offsets. Organized by the pulse type.
        """
        self.pulses = self.channels['ch_name'].values
        self.spikes = self.nidaq[self.pulses].diff()
        self.pulseOnsets = {}
        for pulse in self.pulses:
            if pulse != 'monitor_refresh':
                onsets = self.nidaq['timestamps'][self.spikes[pulse] > threshold].reset_index(drop= True)
                onsetInd = self.nidaq['timestamps'][self.spikes[pulse] > threshold].index
                offsets = self.nidaq['timestamps'][self.spikes[pulse] < -threshold].reset_index(drop= True)
                offsetInd = self.nidaq['timestamps'][self.spikes[pulse] < -threshold].index

                # Sometimes it starts with stim on
                if len(onsets.dropna(axis= 0)) < len(offsets.dropna(axis= 0)):
                    offsets = offsets.drop([0]).reset_index(drop= True)
                    offsetInd = offsetInd[1:]

            self.pulseOnsets[pulse] = pd.concat([onsets, offsets], axis= 1)
            self.pulseOnsets[pulse].columns = ['onsets', 'offsets']
            self.pulseOnsets[pulse]['onsetInd'] = onsetInd
            self.pulseOnsets[pulse]['offsetInd'] = offsetInd

            if pulse == 'visual_stimulus':
                dur = self.pulseOnsets[pulse]['offsets'] - self.pulseOnsets[pulse]['onsets']
                ind = dur[dur > dur.mean() + dur.std()].index
                # print 'len', len(self.pulseOnsets[pulse]), 'ind', ind
                self.pulseOnsets[pulse] = self.pulseOnsets[pulse].drop(ind).reset_index(drop= True)
                # print 'then len', len(self.pulseOnsets[pulse])

    def getOnsets(self, threshold= 2.0, save= False):
        """
        Find the event onsets and offsets.
        """
        self.pulses = self.channels['ch_name'].values
        self.spikes = self.nidaq.copy()
        self.spikes[self.pulses] = self.nidaq[self.pulses].diff()
        self.onsetMatrix = self.spikes.copy()
        self.offsetMatrix = self.spikes.copy()
        for pulse in self.pulses:
            self.onsetMatrix[pulse] = (self.spikes[pulse] > threshold) * 1
            self.offsetMatrix[pulse] = (self.spikes[pulse] < -threshold) * 1
            # Sometimes it starts with stim on
            while len(self.onsetMatrix[pulse] > 0) < len(self.offsetMatrix[pulse] > 0):
                ind = self.offsetMatrix[pulse][self.offsetMatrix[pulse] > 0].index[0]
                self.offsetMatrix[pulse][self.offsetMatrix[pulse] > 0] = 0


if __name__ == '__main__':
    exp = behIO('LR13', '180622', [1,2,3])
    exp.setDir('/Volumes/User Folders/Trent/MixedValenceBehavior')
    exp.loadRuns('nidaq', [1,3])
