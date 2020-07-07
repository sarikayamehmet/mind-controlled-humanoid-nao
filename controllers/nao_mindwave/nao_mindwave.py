# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 15:20:12 2020

@author: MAS
"""

from controller import Robot, Motion, Keyboard
import numpy as np
import subprocess
import sys

class Nao (Robot):
    PHALANX_MAX = 8
    
    def startMindwave(self):
        self.outfile="data_eeg.csv";
        p = subprocess.Popen([sys.executable, 'nao_mindwave_reader.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    # load motion files
    def loadMotionFiles(self):
        self.handWave = Motion('../../motions/HandWave.motion')
        self.forwards = Motion('../../motions/Forwards50.motion')
        self.backwards = Motion('../../motions/Backwards.motion')
        self.sideStepLeft = Motion('../../motions/SideStepLeft.motion')
        self.sideStepRight = Motion('../../motions/SideStepRight.motion')
        self.turnLeft60 = Motion('../../motions/TurnLeft60.motion')
        self.turnRight60 = Motion('../../motions/TurnRight60.motion')

    def startMotion(self, motion):
        # interrupt current motion
        if self.currentlyPlaying:
            self.currentlyPlaying.stop()

        # start new motion
        motion.play()
        self.currentlyPlaying = motion

    def setAllLedsColor(self, rgb):
        # these leds take RGB values
        for i in range(0, len(self.leds)):
            self.leds[i].set(rgb)

        # ear leds are single color (blue)
        # and take values between 0 - 255
        self.leds[5].set(rgb & 0xFF)
        self.leds[6].set(rgb & 0xFF)

    def setHandsAngle(self, angle):
        for i in range(0, self.PHALANX_MAX):
            clampedAngle = angle
            if clampedAngle > self.maxPhalanxMotorPosition[i]:
                clampedAngle = self.maxPhalanxMotorPosition[i]
            elif clampedAngle < self.minPhalanxMotorPosition[i]:
                clampedAngle = self.minPhalanxMotorPosition[i]

            if len(self.rphalanx) > i and self.rphalanx[i] is not None:
                self.rphalanx[i].setPosition(clampedAngle)
            if len(self.lphalanx) > i and self.lphalanx[i] is not None:
                self.lphalanx[i].setPosition(clampedAngle)

    def findAndEnableDevices(self):
        # get the time step of the current world.
        self.timeStep = int(self.getBasicTimeStep())

        # camera
        self.cameraTop = self.getCamera("CameraTop")
        self.cameraBottom = self.getCamera("CameraBottom")
        self.cameraTop.enable(4 * self.timeStep)
        self.cameraBottom.enable(4 * self.timeStep)

        # accelerometer
        self.accelerometer = self.getAccelerometer('accelerometer')
        self.accelerometer.enable(4 * self.timeStep)

        # gyro
        self.gyro = self.getGyro('gyro')
        self.gyro.enable(4 * self.timeStep)

        # gps
        self.gps = self.getGPS('gps')
        self.gps.enable(4 * self.timeStep)

        # inertial unit
        self.inertialUnit = self.getInertialUnit('inertial unit')
        self.inertialUnit.enable(self.timeStep)

        # ultrasound sensors
        self.us = []
        usNames = ['Sonar/Left', 'Sonar/Right']
        for i in range(0, len(usNames)):
            self.us.append(self.getDistanceSensor(usNames[i]))
            self.us[i].enable(self.timeStep)

        # foot sensors
        self.fsr = []
        fsrNames = ['LFsr', 'RFsr']
        for i in range(0, len(fsrNames)):
            self.fsr.append(self.getTouchSensor(fsrNames[i]))
            self.fsr[i].enable(self.timeStep)

        # foot bumpers
        self.lfootlbumper = self.getTouchSensor('LFoot/Bumper/Left')
        self.lfootrbumper = self.getTouchSensor('LFoot/Bumper/Right')
        self.rfootlbumper = self.getTouchSensor('RFoot/Bumper/Left')
        self.rfootrbumper = self.getTouchSensor('RFoot/Bumper/Right')
        self.lfootlbumper.enable(self.timeStep)
        self.lfootrbumper.enable(self.timeStep)
        self.rfootlbumper.enable(self.timeStep)
        self.rfootrbumper.enable(self.timeStep)

        # there are 7 controlable LED groups in Webots
        self.leds = []
        self.leds.append(self.getLED('ChestBoard/Led'))
        self.leds.append(self.getLED('RFoot/Led'))
        self.leds.append(self.getLED('LFoot/Led'))
        self.leds.append(self.getLED('Face/Led/Right'))
        self.leds.append(self.getLED('Face/Led/Left'))
        self.leds.append(self.getLED('Ears/Led/Right'))
        self.leds.append(self.getLED('Ears/Led/Left'))

        # get phalanx motor tags
        # the real Nao has only 2 motors for RHand/LHand
        # but in Webots we must implement RHand/LHand with 2x8 motors
        self.lphalanx = []
        self.rphalanx = []
        self.maxPhalanxMotorPosition = []
        self.minPhalanxMotorPosition = []
        for i in range(0, self.PHALANX_MAX):
            self.lphalanx.append(self.getMotor("LPhalanx%d" % (i + 1)))
            self.rphalanx.append(self.getMotor("RPhalanx%d" % (i + 1)))

            # assume right and left hands have the same motor position bounds
            self.maxPhalanxMotorPosition.append(self.rphalanx[i].getMaxPosition())
            self.minPhalanxMotorPosition.append(self.rphalanx[i].getMinPosition())

        # shoulder pitch motors
        self.RShoulderPitch = self.getMotor("RShoulderPitch")
        self.LShoulderPitch = self.getMotor("LShoulderPitch")

        # keyboard
        self.keyboard = self.getKeyboard()
        self.keyboard.enable(10 * self.timeStep)

    def __init__(self):
        Robot.__init__(self)
        self.currentlyPlaying = False
        # initialize stuff
        self.findAndEnableDevices()
        self.loadMotionFiles()
        self.startMindwave()

    def getWaves(self):
        poorSignalLevel=blinkStrength=attention=meditation=0
        with open(self.outfile,'rb') as f:
            lines = f.readlines()
        f.close()
        last5 = np.genfromtxt(lines[-3:],delimiter=',')
        poorSignalLevel = last5[:,0]
        blinkStrength = last5[:,1]
        attention = last5[:,2]
        meditation = last5[:,3]
        poors = sum(poorSignalLevel>0)
        blinks = sum(blinkStrength>40)
        att = sum(attention>50)
        med = sum(meditation<40)
        #print(str(blinks)+","+str(att))
        return poors, blinks, att, med
        
    def run(self):
        #self.handWave.setLoop(True)
        self.handWave.play()       
        self.handWave.setLoop(False)
        turnAround = True
        
        while True:
            poorSignalLevel, blink_count, attention_count, meditation_count = self.getWaves()

            if poorSignalLevel > 0:
                self.setAllLedsColor(0xff0000)  # red
                print("poor signal!!!")
            elif (blink_count > 0) and turnAround:
                print("turn around")
                self.setAllLedsColor(0x00ff00)  # green
                while turnAround:
                    for k in range(3*self.timeStep):
                        self.startMotion(self.turnRight60)
                        robot.step(self.timeStep)
                    poorSignalLevel, blink_count, attention_count, meditation_count = self.getWaves()
                    if blink_count > 0:
                        print("exit loop")
                        turnAround = False
            elif attention_count > 0:
                print("go forward")
                turnAround = True
                self.setAllLedsColor(0x0000ff)  # blue
                for k in range(3*self.timeStep):
                    self.startMotion(self.forwards)
                    robot.step(self.timeStep)  
            elif meditation_count > 0:
                self.setAllLedsColor(0x000000)  # off
                #print("i am not cool")

            if robot.step(self.timeStep) == -1:
                break
            
        self.sock.close()


# create the Robot instance and run main loop
robot = Nao()
robot.run()
