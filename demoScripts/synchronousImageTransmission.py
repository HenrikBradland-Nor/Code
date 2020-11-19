# Make sure to have CoppeliaSim running, with followig scene loaded:
#
# scenes/synchronousImageTransmissionViaRemoteApi.ttt
#
# Do not launch simulation, but run this script
#
# The client side (i.e. this script) depends on:
#
# sim.py, simConst.py, and the remote API library available
# in programming/remoteApiBindings/lib/lib

try:
    import sim_code
except:
    print ('--------------------------------------------------------------')
    print ('"sim.py" could not be imported. This means very probably that')
    print ('either "sim.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "sim.py"')
    print ('--------------------------------------------------------------')
    print ('')

import math
import time

class Client:
    def __enter__(self):
        self.intSignalName='legacyRemoteApiStepCounter'
        self.stepCounter=0
        self.lastImageAcquisitionTime=-1
        sim_code.simxFinish(-1) # just in case, close all opened connections
        self.id=sim_code.simxStart('127.0.0.1', 19997, True, True, 5000, 5) # Connect to CoppeliaSim
        return self
    
    def __exit__(self,*err):
        sim_code.simxFinish(-1)

with Client() as client:
    client.runInSynchronousMode=True
    
    print("running")

    if client.id!=-1:
        print ('Connected to remote API server')

        def stepSimulation():
            if client.runInSynchronousMode:
                currentStep=client.stepCounter
                sim_code.simxSynchronousTrigger(client.id);
                while client.stepCounter==currentStep:
                    retCode,s=sim_code.simxGetIntegerSignal(client.id, client.intSignalName, sim_code.simx_opmode_buffer)
                    if retCode==sim_code.simx_return_ok:
                        client.stepCounter=s
                retCode,res,img=sim_code.simxGetVisionSensorImage(client.id, client.visionSensorHandle, 0, sim_code.simx_opmode_buffer)
                client.lastImageAcquisitionTime=sim_code.simxGetLastCmdTime(client.id)
                if retCode==sim_code.simx_return_ok:
                   sim_code.simxSetVisionSensorImage(client.id, client.passiveVisionSensorHandle, img, 0, sim_code.simx_opmode_oneshot)
            else:
                retCode,res,img=sim_code.simxGetVisionSensorImage(client.id, client.visionSensorHandle, 0, sim_code.simx_opmode_buffer)
                if retCode==sim_code.simx_return_ok:
                    imageSimTime=sim_code.simxGetLastCmdTime(client.id)
                    if client.lastImageAcquisitionTime!=imageSimTime:
                        client.lastImageAcquisitionTime=imageSimTime
                        sim_code.simxSetVisionSensorImage(client.id, client.passiveVisionSensorHandle, img, 0, sim_code.simx_opmode_oneshot)

        # Start streaming client.intSignalName integer signal, that signals when a step is finished:
        sim_code.simxGetIntegerSignal(client.id, client.intSignalName, sim_code.simx_opmode_streaming)
        
        res,client.visionSensorHandle=sim_code.simxGetObjectHandle(client.id, 'VisionSensor', sim_code.simx_opmode_blocking)
        res,client.passiveVisionSensorHandle=sim_code.simxGetObjectHandle(client.id, 'PassiveVisionSensor', sim_code.simx_opmode_blocking)
        
        # Start streaming the vision sensor image:
        sim_code.simxGetVisionSensorImage(client.id, client.visionSensorHandle, 0, sim_code.simx_opmode_streaming)
        
        # enable the synchronous mode on the client:
        if client.runInSynchronousMode:
            sim_code.simxSynchronous(client.id, True)

        sim_code.simxStartSimulation(client.id, sim_code.simx_opmode_oneshot)
        
        startTime=time.time()
        while time.time()-startTime < 5:
            stepSimulation()
        
        # stop data streaming
        sim_code.simxGetIntegerSignal(client.id, client.intSignalName, sim_code.simx_opmode_discontinue)
        sim_code.simxGetVisionSensorImage(client.id, client.visionSensorHandle, 0, sim_code.simx_opmode_discontinue)
        
        sim_code.simxStopSimulation(client.id, sim_code.simx_opmode_blocking)
