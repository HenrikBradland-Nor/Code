from myCode import *
import time
from sim import *
import numpy as np

X_AXIS = 0
Y_AXIS = 1
Z_AXIS = 2


class API():

    def __init__(self, step_time):

        self.step_time = step_time
        self.step_coundt = 0

        self.snake_head_handel = -1
        self.snake_tail_handel = -1
        self.snake_joint_cam_handel = -1
        self.snake_joint_h_handel = []
        self.snake_joint_v_handel = []
        self.snake_joint_all_handel = []

    def startConection(self):
        simxFinish(-1)
        self.clientID = simxStart('127.0.0.1', 19999, True, True, 5000, 5)  # Connect to CoppeliaSim
        if self.clientID != -1:
            print("Connected to API server")
        else:
            print("Failed to connect to API server")
            sys.exit("Could not connect")
        return self.clientID

    def stopConection(self):
        e1 = simxGetPingTime(self.clientID)
        e2 = simxFinish(self.clientID)
        print("Simulation ended")
        return [e1, e2]

    def setClienID(self, clientID):
        self.clientID = clientID

    def steppingMode(self, on=True):
        e = simxSynchronous(self.clientID, on)
        print("Stepping mode activated")
        return e

    def nextStep(self):
        e = simxSynchronousTrigger(self.clientID)
        self.step_coundt += 1
        return e

    def setUpHandle(self):
        error = []
        eC, self.snake_joint_cam_handel = simxGetObjectHandle(self.clientID, "snake_joint_cam", simx_opmode_blocking)
        eB, self.snake_head_handel = simxGetObjectHandle(self.clientID, "snake_body1", simx_opmode_blocking)
        eT, self.snake_tail_handel = simxGetObjectHandle(self.clientID, "snake_body16", simx_opmode_blocking)
        self.snake_joint_v_handel.append(self.snake_joint_cam_handel)
        self.snake_joint_all_handel.append(self.snake_joint_cam_handel)
        error.append(eC)
        for i in range(7):
            eH, h = simxGetObjectHandle(self.clientID, "snake_joint_h" + str(i + 1), simx_opmode_blocking)
            eV, v = simxGetObjectHandle(self.clientID, "snake_joint_v" + str(i + 1), simx_opmode_blocking)
            self.snake_joint_h_handel.append(h)
            self.snake_joint_v_handel.append(v)
            self.snake_joint_all_handel.append(v)
            self.snake_joint_all_handel.append(h)
            error.append(eH)
            error.append(eV)
        print("Handles set up")
        print("Vertical handler: \n", self.snake_joint_v_handel)
        print("Horisontal handler: \n", self.snake_joint_h_handel)
        return error

    def resetSimulation(self):
        self.step_coundt = 0
        simxStopSimulation(self.clientID, simx_opmode_blocking)
        print("Stopping simulation")
        time.sleep(1)
        simxStartSimulation(self.clientID, simx_opmode_blocking)

    def _degToRad(self, deg):
        return deg * np.pi / 180

    def _position(self, action, index):
        action = self._degToRad(action)
        ampletude = action[0]
        phase = action[1]
        speed = action[2]
        return ampletude * np.sin(speed * (self.step_time * self.step_coundt) + phase * index)

    def setJointTargetPosition(self, action):
        error = []
        action_v = action[:3]
        action_h = action[3:]

        for ii in range(len(self.snake_joint_h_handel)):
            e = simxSetJointTargetPosition(self.clientID,
                                           self.snake_joint_h_handel[ii],
                                           self._position(action_h, ii),
                                           simx_opmode_streaming)
            error.append(e)

        for ii in range(len(self.snake_joint_v_handel)):
            e = simxSetJointTargetPosition(self.clientID,
                                           self.snake_joint_v_handel[ii],
                                           self._position(action_v, ii),
                                           simx_opmode_streaming)
            error.append(e)
        return error

    def getJointPosition(self):
        pos = []
        error = []
        for ii in range(len(self.snake_joint_all_handel)):
            e, p = simxGetJointPosition(self.clientID,
                                        self.snake_joint_all_handel[ii],
                                        simx_opmode_streaming)
            pos.append(p)
            error.append(e)
        return pos

    def getHeadOrientation(self):
        _, orientation = simxGetObjectOrientation(self.clientID, self.snake_head_handel, -1, simx_opmode_streaming)
        return orientation[2]

    def getHeadVelocity(self):
        _, vel, ang = simxGetObjectVelocity(self.clientID, self.snake_head_handel, simx_opmode_streaming)
        return vel[1]

    def getHeadAbsolutPosition(self):
        _, pos = simxGetObjectPosition(self.clientID, self.snake_head_handel, -1, simx_opmode_streaming)
        return pos

    def getTailAbsolutPosition(self):
        _, pos = simxGetObjectPosition(self.clientID, self.snake_tail_handel, -1, simx_opmode_streaming)
        return pos