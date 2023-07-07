import pygame
import math
import numpy as np


def uncertainty_add(dis, angle, sigma):  # dis = mean, uncertainty = variance of gaussian distribution
    mean = np.array([dis, angle])
    covariance = np.diag(sigma ** 2)
    dis, angle = np.random.multivariate_normal(mean, covariance)
    dis = max(dis, 0)
    angle = max(angle, 0)
    return [dis, angle]


class LaserSensor:

    def __init__(self, Range, map, uncertainty):
        self.Range = Range
        self.speed = 4  # rounds per sec
        self.sigma = np.array([uncertainty[0], uncertainty[1]])  # sensor measurement noise
        self.pos = (0, 0)

        self.map = map
        self.W, self.H = pygame.display.get_surface().get_size()
        self.senseObstacles = []

    def distance(self, obs_pos):
        px = (obs_pos[0] - self.pos[0]) ** 2
        py = (obs_pos[1] - self.pos[1]) ** 2
        return math.sqrt(px + py)

    def sense_obs(self):
        data = []
        x1, y1 = self.pos[0], self.pos[1]
        for angle in np.linspace(0, 2*math.pi, 60, False):  # from 0 to 360 deg
            x2, y2 = (x1 + self.Range * math.cos(angle),
                      y1 - self.Range * math.sin(angle))
            for i in range(0, 100):
                u = i / 100
                x = int(x2 * u + x1 * (1-u))  # interpolation
                y = int(y2 * u + y1 * (1-u))
                if 0 < x < self.W and 0 < y < self.H:
                    color = self.map.get_at((x, y))
                    if(color[0], color[1], color[2]) == (0, 0, 0):
                        distance = self.distance((x, y))
                        output = uncertainty_add(distance, angle, self.sigma)
                        output.append(self.pos)

                        # store the measurements
                        data.append(output)
                        break

        if len(data) > 0:
            return data

        else:
            return False
