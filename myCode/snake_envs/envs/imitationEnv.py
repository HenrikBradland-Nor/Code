import gym
from gym import error, spaces, utils
from gym.utils import seeding
import pandas as pd
import os

import torch
import torch.nn as nn

import numpy as np
import random

MAX_STEPS = 20000
STEP_TIME = 50 # Time in ms
MAX_NUM_POS_SPEED_CALCULATION = 10

FILE_SPLITTER = 15

dataPath = "C:/Users/Henrik_Brådland/Google Drive/Studier/Semester 9/IKT446 - Seminar 4/Code/myCode/Imitation_TrainningFiles"



class ImitationEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    self.corect_actions = self._updateDataFile()

    self.stepCount = 1

    self.loss = nn.MSELoss()

    self.headPos = []

    '''
    Ampletude_v, Phase_v, AngVel_v, Ampletude_h, Phase_h, AngVel_h
    All values in [deg] or [deg/sec]
    '''

    self.action_space = spaces.Box(
      low=np.array([0, 0, 0, 0, 0, 0]),
      high=np.array([48, 450, 500, 48, 450, 500]),
      dtype=np.float64)

    '''
    All observations are from the space of -90 to +90 [deg]
    The observations are looked back in time three iterations
    '''

    self.obs_shape = [3, 15+1+1]
    self.observation_space = spaces.Box(
      low=-np.pi/2,
      high=np.pi/2,
      shape=self.obs_shape,
      dtype=np.float64)


  def _updateDataFile(self):
    curentPath = os.path.abspath(os.getcwd())
    os.chdir(dataPath)

    files = os.listdir()
    r = random.randint(0, len(files)-1)
    pb_read = pd.read_csv(files[r])

    A, P, S = files[r].split('_')
    A = A.replace('A', '')
    P = P.replace('P', '')
    S = S.replace('S', '')

    os.chdir(curentPath)

    self.df = np.asarray(pb_read)

    return np.array([A, P, S, 0, 0, 0], dtype=np.float64)

  def step(self, action):
    action_hat =  self.corect_actions
    for ii in range(len(self.action_space.high)):
      action[ii] /= self.action_space.high[ii]
      action_hat[ii] /= self.action_space.high[ii]

    reward = 1-self.loss(torch.tensor(action), torch.tensor(action_hat)).item()

    self.stepCount += 1
    ob = []
    for ii in range(self.obs_shape[0]):
      index = self.stepCount-ii
      if index >= 0:
        pos = self.df[index][:FILE_SPLITTER]
        pos = np.concatenate((pos, np.array([0,1], dtype=np.float64)), axis=None)
        ob.append(pos)
      else:
        ob.append(np.zeros((FILE_SPLITTER+2,), dtype=np.float64))

    done = self.stepCount >= len(self.df)-1

    return np.asarray(ob), reward, done, {}

  def reset(self):
    self.stepCount = 1
    self.corect_actions = self._updateDataFile()
    return self.step(np.array([0, 0, 0, 0, 0, 0]))[0]

  def render(self, mode='human'):
    print("Hello world!")
