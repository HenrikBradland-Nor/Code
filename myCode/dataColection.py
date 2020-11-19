from sim import *
import sim
import sys
import time
import math
import random

import matplotlib.pyplot as plt


def degToRad(deg):
    return deg * math.pi / 180


print('Program started')

simxFinish(-1)  # just in case, close all opened connections
clientID = simxStart('127.0.0.1', 19999, True, False, 5000, 5)  # C

# onnect to CoppeliaSim
print("ClientID is: ", clientID)
if clientID != -1:

    simxSynchronous(clientID, True)
    time.sleep(1)

    snake_joint_handel = []
    errorCodeHandelCam, snake_joint_cam_handel = simxGetObjectHandle(clientID, "snake_joint_cam", simx_opmode_blocking)
    snake_joint_handel.append(snake_joint_cam_handel)

    _, snake_head_handel = simxGetObjectHandle(clientID, "snake_body1", simx_opmode_blocking)

    for i in range(7):
        errorCodeHandelH, h = simxGetObjectHandle(clientID, "snake_joint_h" + str(i + 1), simx_opmode_blocking)
        errorCodeHandelV, v = simxGetObjectHandle(clientID, "snake_joint_v" + str(i + 1), simx_opmode_blocking)
        snake_joint_handel.append(v)
        snake_joint_handel.append(h)

    EPOCH = 500

    headPos = []
    MAX_NUM_POS_SPEED_CALCULATION = 10
    STEP_TIME = 0.05

    Velocity = []
    Step = []
    xPos = []
    yPos = []
    zPos = []

    time.sleep(1)
    number_of_sucsesses = 0
    target_number_of_sucsesses = 500

    while number_of_sucsesses < target_number_of_sucsesses:
        amplitude_deg = random.randrange(30, 48) # [deg]
        phase_deg = random.randrange(20, 600) - 150  # [deg]
        speed_deg = random.randrange(100, 500)  # [deg/sec]

        amplitude = degToRad(amplitude_deg)
        phase = degToRad(phase_deg)
        speed = degToRad(speed_deg)

        all_pos = []
        e = simxStartSimulation(clientID, simx_opmode_blocking)
        print("Starting simulation")
        for t in range(EPOCH):

            pos = []
            for ii in range(len(snake_joint_handel)):
                r, p = simxGetJointPosition(clientID,
                                            snake_joint_handel[ii],
                                            simx_opmode_streaming)
                r, v, ang_v = simxGetObjectVelocity(clientID,
                                                    snake_joint_handel[ii],
                                                    simx_opmode_streaming)
                pos.append(p)
                pos.append(ang_v[0])

            for ii in range(len(snake_joint_handel)):
                if ii == 0 or ii % 2 == 1:
                    tp = amplitude * math.sin(speed * (t * STEP_TIME) + phase * ii)
                else:
                    tp = 0
                simxSetJointTargetPosition(clientID, snake_joint_handel[ii], tp, simx_opmode_streaming)
                pos.append(tp)

            all_pos.append(pos)

            error = simxSynchronousTrigger(clientID)

            if len(headPos) >= MAX_NUM_POS_SPEED_CALCULATION:
                headPos.pop(0)
            e, pos = simxGetObjectPosition(clientID, snake_joint_cam_handel, -1, simx_opmode_streaming)
            headPos.append(pos[1])

            distance = headPos[len(headPos) - 1] - headPos[0]
            v = distance / (len(headPos) * STEP_TIME)



        for ii in range(len(snake_joint_handel)):
            simxSetJointPosition(clientID, snake_joint_handel[ii], 0, simx_opmode_streaming)

        if max(yPos) - abs(max(xPos)) > 1 and max(zPos) < .5:
            print("SUCSESS:", str(number_of_sucsesses) + "/" + str(target_number_of_sucsesses))

            sub_dirs = os.listdir()
            name = "A" + str(amplitude_deg) + "_P" + str(phase_deg) + "_S" + str(speed_deg)

            for dir in sub_dirs:
                if 'ImitationTrainningFiles' in dir:
                    os.chdir(dir)
                    file1 = open(name, "w+")
                    for pos in all_pos:
                        for ii in range(len(pos)):
                            if ii == len(pos) - 1:
                                file1.writelines(str(pos[ii]) + "\n")
                            else:
                                file1.writelines(str(pos[ii]) + ", ")
                    file1.close()
                    number_of_sucsesses = len(os.listdir())
                    os.chdir("..")

        simxStopSimulation(clientID, simx_opmode_blocking)
        print("Stopping simulation")
        time.sleep(1)

        print("\n===========================================",
              "\nAmplitude:", amplitude_deg, "[deg]", "\nPhase:", phase_deg, "[deg]", "\nSpeed:", speed_deg,
              "[deg/sec]",
              "\n-------------------------------------------",
              "\nTotal time:", int(STEP_TIME * EPOCH), "[s]",
              "\nMax: %.3f [m/s]" % max(Velocity),
              "\nAvg: %.3f [m/s]" % (sum(Velocity[15:]) / len(Velocity[15:])),
              "\nDis: %.3f [m]" % yPos[len(yPos) - 1],
              "\nScore: %.3f [m]" % (yPos[len(yPos) - 1] - abs(xPos[len(xPos) - 1])),
              "\n===========================================\n")

    # Before closing the connection to CoppeliaSim, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    simxStopSimulation(clientID, simx_opmode_blocking)
    simxGetPingTime(clientID)

    # Now close the connection to CoppeliaSim:
    simxFinish(clientID)

    plt.figure()
    plt.plot(Step, Velocity)
    # plt.show()

else:
    print('Conceton Failed')

    sys.exit("Could not connect")

print('Program ended')
