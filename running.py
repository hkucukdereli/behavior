import numpy as np
import pandas as pd

def resample(position, framerate= 20, wheel_dia= 14, wheel_tabs=44):
    newPos = []
    pos = 0
    for i in np.arange(0, position['timestamp'].iloc[-1], 100):
        posBin = position['value'][position['timestamp'] < i+1]
        if len(posBin):
            pos = posBin.iloc[-1]
        newPos.append(pos)

    timeNew = np.arange(0, position['timestamp'].iloc[-1]+1, 100)
    speed = runningSpeed(newPos, framerate, wheel_dia, wheel_tabs)

    running = pd.DataFrame([])
    running['position'] = newPos
    running['speed'] = speed
    running['timestamp'] = timeNew

    return running

def runningSpeed(position, framerate= 100, wheel_dia= 14, wheel_tabs= 44):
    """
    position: array
    wheel_dia: in cm
    """

    wheel_circ = wheel_dia*math.pi
    step_size = wheel_circ/(wheel_tabs*2)

    speed = np.zeros(len(position))
    speed[1:] = np.diff(position)
    speed = speed * step_size * framerate

    speed = np.convolve(speed, np.ones(int(np.ceil(framerate))) / np.ceil(framerate), 'same')

    return speed
