from sim import *
import sys
import time
import numpy as np

import matplotlib.pyplot as plt


print ('Program started')

simxFinish(-1) # just in case, close all opened connections
clientID=simxStart('127.0.0.1', 19999, True, True, 5000, 5) # Connect to CoppeliaSim
print("ClientID is: ", clientID)
if clientID!=-1:

    #sim.simxSynchronous(clientID, True)
    #sim.simxStartSimulation(clientID,sim.simx_opmode_oneshot)
    simxStartSimulation(clientID, simx_opmode_oneshot)
    #time.sleep(2)
    snake_joint_h_handel = []
    snake_joint_v_handel = []
    _, snake_joint_cam_handel = simxGetObjectHandle(clientID, "snake_joint_cam", simx_opmode_blocking)
    _, snake_head_handel = simxGetObjectHandle(clientID, "snake_body1", simx_opmode_blocking)
    for i in range(7):
        errorCodeHandelH, h = simxGetObjectHandle(clientID, "snake_joint_h" + str(i+1), simx_opmode_blocking)
        errorCodeHandelV, v = simxGetObjectHandle(clientID, "snake_joint_v" + str(i+1), simx_opmode_blocking)
        snake_joint_h_handel.append(h)
        snake_joint_v_handel.append(v)

    for x in range(20):
        for ii in range(len(snake_joint_h_handel)):
            tp = 1 * np.sin(2 * (x * 0.1) + 1 * ii)
            simxSetJointTargetPosition(clientID, snake_joint_h_handel[ii], tp, simx_opmode_streaming)
        _, vel, ang = simxGetObjectVelocity(clientID, snake_head_handel, simx_opmode_streaming)
        print(vel)
        time.sleep(0.1)
    all_pos = []
    all_torque = []
    tot = []
    '''
    for i in range(6):


        v = 0
        if i%2==0:
            v = -0.15
            #print("Negative velocity")
        else:
            v = 0.15
            #print("Positive velocity")
        if i==5:
            v = 0

        for i in range(4):
            curent = snake_joint_v_handel[i]
            errorCodeVelocityCam = sim.c_SetJointTargetPosition(clientID, curent, v, sim.simx_opmode_streaming)


        t = time.time()
        while time.time() - t < 2:
            e, pos = sim.simxGetObjectPosition(clientID, snake_joint_cam_handel, -1, sim.simx_opmode_streaming)
            #f, torque = sim.simxGetJointForce(clientID, snake_joint_cam_handel, sim.simx_opmode_streaming)
            g, matrix = sim.simxGetJointMatrix(clientID, snake_joint_cam_handel, sim.simx_opmode_streaming)


            all_pos.append(pos[2])
            #all_torque.append(torque)
            tot.append(time.time())

        print(pos)

    #ScenePath = "C:/Users/Henrik_Brådland/Google Drive/Studier/Semester 9/IKT446 - Seminar 4/SimFileSnake.ttt"

    

    #sim.simxSetObjectPosition(clientID, snake_joint_cam_handel, -1, startPos, sim.simx_opmode_oneshot)

    #print(e)

    n = 0
    for ii in range(len(all_pos)):
        if all_pos[ii] == 0:
            n += 1
    #print("Number of zeroes:", n)


    plt.figure()
    plt.plot(tot[n:], all_pos[n:])#, 'b', tot, all_torque, 'r')
    plt.show()

    print("min:", min(all_pos[n:]), "max:", max(all_pos[n:]))

    '''
    # Before closing the connection to CoppeliaSim, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    simxGetPingTime(clientID)

    # Now close the connection to CoppeliaSim:
    simxFinish(clientID)
else:
    print('Conceton Failed')
    sys.exit("Could not connect")

print ('Program ended')