import random
import json
import gym
from gym import spaces
import numpy as np

import APIconections as API

MAX_PENALTY = -100
MAX_REWARD = 500

REWARD_INTERWALL = 0.1
REWARD_PER_INTERWALL = 10

STEP_TIME = 50  # Time in ms
MAX_STEPS = 500

J_LOW = -np.pi / 2
J_HIGH = np.pi / 2

X_BOUNDS = np.array([-0.5, 0.5], dtype=np.float64)
Y_BOUNDS = np.array([-0.2, np.inf], dtype=np.float64)
Z_BOUNDS = np.array([-0.1, 0.5], dtype=np.float64)
ANG_BOUND = np.array([-np.pi/3, np.pi/3], dtype=np.float64)

class SnakeEnv(gym.Env):
    """A Snake robot environment for OpenAI gym"""
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(SnakeEnv, self).__init__()

        self.api = API.API(STEP_TIME)
        self.clientID = self.api.startConection()
        self.api.steppingMode(True)
        self.api.setUpHandle()

        self.reward_range = (MAX_PENALTY, MAX_REWARD)

        self.stepCount = 0

        self.nextReward = 0
        self.rewardInterwall = REWARD_INTERWALL
        self.rewardPerInterwall = REWARD_PER_INTERWALL

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
            low=np.array([[J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, -np.pi, -np.inf],
                          [J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, -np.pi, -np.inf],
                          [J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, J_LOW, -np.pi, -np.inf]]),
            high=np.array([[J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, np.pi, np.inf],
                           [J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, np.pi, np.inf],
                           [J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, J_HIGH, np.pi, np.inf]]),
            dtype=np.float64)
        self.jointPositions = np.zeros(self.obs_shape, dtype=np.float64)

    def _setUp(self, clientID):
        self.clientID = clientID
        print("Client ID is set to: ", self.clientID)

    def _updateObservation(self):
        for ii in range(len(self.obs_shape) - 1):
            self.jointPositions[ii] = self.jointPositions[ii + 1]
        self.jointPositions[len(self.obs_shape) - 1] = np.concatenate((np.array(self.api.getJointPosition(), dtype=np.float64),
                                                                       np.array(self.api.getHeadOrientation(), dtype=np.float64),
                                                                       np.array(self.api.getHeadVelocity(), dtype=np.float64)), axis=None)


    def _bodyWithinBounds(self, headPos, tailPos):
        x_h = X_BOUNDS[0] <= headPos[API.X_AXIS] <= X_BOUNDS[1]
        y_h = Y_BOUNDS[0] <= headPos[API.Y_AXIS] <= Y_BOUNDS[1]
        z_h = Z_BOUNDS[0] <= headPos[API.Z_AXIS] <= Z_BOUNDS[1]

        x_t = X_BOUNDS[0] <= tailPos[API.X_AXIS] <= X_BOUNDS[1]
        y_t = Y_BOUNDS[0] <= tailPos[API.Y_AXIS] <= Y_BOUNDS[1]
        z_t = Z_BOUNDS[0] <= tailPos[API.Z_AXIS] <= Z_BOUNDS[1]

        return x_h and y_h and z_h and x_t and y_t and z_t

    def _calculateReward(self):
        tailPos = self.api.getTailAbsolutPosition()
        headPos = self.api.getHeadAbsolutPosition()
        headAng = self.api.getHeadOrientation()
        reward = 0
        if headPos[API.Y_AXIS] > self.nextReward:
            reward += self.rewardPerInterwall
            self.nextReward += self.rewardInterwall

        if not self._bodyWithinBounds(headPos, tailPos):
            reward += MAX_PENALTY

        if not ANG_BOUND[0] <= headAng <= ANG_BOUND[1]:
            reward += MAX_PENALTY

        return reward

    def _simulationEnded(self):
        return self.stepCount >= MAX_STEPS

    def step(self, action):
        self.api.setJointTargetPosition(action)
        self.api.nextStep()
        self.stepCount += 1

        self._updateObservation()

        obs = self.jointPositions
        reward = self._calculateReward()
        done = self._simulationEnded()

        return obs, reward, done, {}

    def reset(self):
        # Reset the state of the environment to an initial state
        self.stepCount = 0
        self.api.resetSimulation()
        self.jointPositions = np.zeros(self.obs_shape, dtype=np.float64)
        self._updateObservation()

        return self.jointPositions

    def render(self, mode='human', close=False):
        print("Render")
