import opensim as osim
import math
import numpy as np
from gym import spaces
import os
from environments.osim import OsimEnv

class ArmEnv(OsimEnv):
    ninput = 12
    model_path = os.path.join(os.path.dirname(__file__), '../../models/Arm26_Optimize.osim')

    def __init__(self, visualize = True):
        super(ArmEnv, self).__init__(visualize = visualize)
        self.joints.append(osim.CustomJoint.safeDownCast(self.jointSet.get(0)))
        self.joints.append(osim.CustomJoint.safeDownCast(self.jointSet.get(1)))

    def reset(self):
        self.istep = 0
        if not self.state0:
            self.state0 = self.model.initSystem()
            self.manager = osim.Manager(self.model)
            self.state = osim.State(self.state0)
        else:
            self.state = osim.State(self.state0)

        self.model.equilibrateMuscles(self.state)

        # nullacttion = np.array([0] * self.noutput, dtype='f')
        # for i in range(0, int(math.floor(0.2 / self.stepsize) + 1)):
        #     self.step(nullacttion)

        return [0.0] * self.ninput # self.get_observation()

    def compute_reward(self):
        obs = self.get_observation()
        up = (2*(math.pi**2) - self.angular_dist(obs[0],math.pi)**2 - self.angular_dist(obs[1],0.0)**2)/(2*math.pi**2)
        still = (obs[2]**2 + obs[3]**2) / 400
        return up - still

    def get_observation(self):
        invars = np.array([0] * self.ninput, dtype='f')

        invars[0] = self.joints[0].getCoordinate(0).getValue(self.state)
        invars[1] = self.joints[1].getCoordinate(0).getValue(self.state)

        invars[2] = self.joints[0].getCoordinate(0).getSpeedValue(self.state)
        invars[3] = self.joints[1].getCoordinate(0).getSpeedValue(self.state)

        invars[4] = self.sanitify(self.joints[0].getCoordinate(0).getAccelerationValue(self.state))
        invars[5] = self.sanitify(self.joints[1].getCoordinate(0).getAccelerationValue(self.state))

        pos = self.model.calcMassCenterPosition(self.state)
        vel = self.model.calcMassCenterVelocity(self.state)
        
        invars[6] = pos[0]
        invars[7] = pos[1]
        invars[8] = pos[2]

        invars[9] = vel[0]
        invars[10] = vel[1]
        invars[11] = vel[2]

        return invars

