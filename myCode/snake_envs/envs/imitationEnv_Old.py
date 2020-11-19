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



class ImitationEnv_Old(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):


    self._updateDataFile()

    self.stepCount = 1

    self.loss = nn.MSELoss()

    self.headPos = []

    self.action_space = spaces.Box(
      low=np.array([-3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14,-3.14, -3.14, -3.14, -3.14, -3.14]),
      high=np.array([3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14]),
      dtype=np.float64)

    self.observation_space = spaces.Box(
      low=np.array([-3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14,-3.14, -3.14, -3.14, -3.14, -3.14]),
      high=np.array([3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14]),
      dtype=np.float64)

#    self.observation_space = spaces.Box(
#      low=np.array([-3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14, -3.14]),
#      high=np.array([3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14, 3.14]),
#      dtype=np.float64)

  def _updateDataFile(self):
    curentPath = os.path.abspath(os.getcwd())
    os.chdir(dataPath)

    files = os.listdir()
    r = random.randint(0, len(files)-1)
    pb_read = pd.read_csv(files[r])

    os.chdir(curentPath)

    self.df = np.asarray(pb_read)


  def step(self, action):
    action_hat = self.df[self.stepCount][FILE_SPLITTER:]
    reward = 1-self.loss(torch.tensor(action), torch.tensor(action_hat)).item()

    self.stepCount += 1
    ob = self.df[self.stepCount][:FILE_SPLITTER]

    done = self.stepCount >= len(self.df)-1

    return ob, reward, done, {}

  def reset(self):
    self.stepCount = 1
    self._updateDataFile()


    return self.df[0][:FILE_SPLITTER]

  def render(self, mode='human'):
    print("Hello world!")
