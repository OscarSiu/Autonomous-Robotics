import pygame
import math
import numpy as np


def distance(pt1, pt2):
    pt1 = np.array(pt1)
    pt2 = np.array(pt2)
    return np.linalg.norm(pt1 - pt2)


class Robot:
    def __init__(self, startpos, width):
        self.m2p = 8000  # meters to pixels
        # robot_dimensions
        self.w = width
        self.x = startpos[0]
        self.y = startpos[1]
        self.theta = 0  # heading

        # Speed
        self.vl = 0.01 * self.m2p  # left velocity
        self.vr = 0.01 * self.m2p  # right velocity
        self.maxspeed = 0.02 * self.m2p
        self.minspeed = 0.01 * self.m2p

        self.min_obs_dist = 150
        self.count_down = 5  # sec

    def avoid_obstacles(self, point_cloud, dt):
        closest_obs = None
        dist = np.inf

        if len(point_cloud) > 1:
            for point in point_cloud:
                if dist > distance([self.x, self.y], point):
                    dist = distance([self.x, self.y], point)
                    closest_obs = (point, dist)

            if closest_obs[1] < self.min_obs_dist and self.count_down > 0:
                self.count_down -= dt
                self.move_backward()

            else:
                # reset count down
                self.count_down = 5

                # move forward
                self.move_forward()

    def move_backward(self):
        self.vr = -self.minspeed
        self.vl = -self.minspeed/2

    def move_forward(self):
        self.vr = self.minspeed
        self.vl = self.minspeed

    def kinematics(self, dt):
        self.x += ((self.vl + self.vr) / 2) * math.cos(self.theta) * dt
        self.y -= ((self.vl + self.vr) / 2) * math.sin(self.theta) * dt
        self.theta += (self.vr - self.vl) / self.w * dt

        # reset theta
        if self.theta > 2 * math.pi or self.theta < -2 * math.pi:
            self.theta = 0

        # set max speed
        self.vr = max(min(self.maxspeed, self.vr), self.minspeed)
        self.vl = max(min(self.maxspeed, self.vl), self.minspeed)


class Graphics:
    def __init__(self, dimensions, robotimg, mapimg):
        pygame.init()

        # Colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)

        # ---------------------MAP---------------------
        # graphics
        self.robot = pygame.image.load(robotimg)
        self.map_img = pygame.image.load(mapimg)

        # map dimensions
        self.height, self.width = dimensions

        # window settings
        pygame.display.set_caption("Obstacle Avoidance")
        self.map = pygame.display.set_mode((self.width, self.height))
        self.map.blit(self.map_img, (0, 0))

    def draw_robot(self, x, y, theta):
        rotated = pygame.transform.rotozoom(self.robot, math.degrees(theta), 1)
        rect = rotated.get_rect(center=(x, y))
        self.map.blit(rotated, rect)

    def draw_sensor_data(self, point_cloud):
        for point in point_cloud:
            pygame.draw.circle(self.map, self.red, point, 3, 0)


class Ultrasonic:

    def __init__(self, sensor_range, map):
        self.sensor_range = sensor_range
        self.map_width, self.map_height = pygame.display.get_surface().get_size()
        self.map = map

    def sense_obstacles(self, x, y, theta):
        obstacles = []
        x1, y1 = x, y
        start_angle = theta - self.sensor_range[1]
        finish_angle = theta + self.sensor_range[1]
        for angle in np.linspace(start_angle, finish_angle, 10, False):
            x2 = x1 + self.sensor_range[0] * math.cos(angle)
            y2 = y1 - self.sensor_range[0] * math.sin(angle)

            for i in range(0, 100):
                u = i / 100
                x = int(x2 * u + x1 * (1 - u))
                y = int(y2 * u + y1 * (1 - u))
                if 0 < x < self.map_width and 0 < y < self.map_height:
                    color = self.map.get_at((x, y))
                    self.map.set_at((x, y), (0, 208, 255))
                    if (color[0], color[1], color[2]) == (0, 0, 0):
                        obstacles.append([x, y])
                        break
        return obstacles
