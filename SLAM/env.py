import math
import pygame


class build_env:
    def __init__(self, mapdim):
        pygame.init()

        self.pointcloud = []
        self.externalMap = pygame.image.load('floorplan.png')
        self.maph, self.mapw = mapdim

        pygame.display.set_caption("SLAM path planning")
        self.map = pygame.display.set_mode((self.mapw, self.maph))
        self.map.blit(self.externalMap, (0, 0))

        # colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.grey = (70, 70, 70)

    def AD2pos(self, dis, angle, robot_pos):
        x = dis * math.cos(angle) + robot_pos[0]
        y = - dis * math.sin(angle) + robot_pos[1]
        return (int(x), int(y))

    def dataStorage(self, data):
        print(len(self.pointcloud))
        for element in data:
            point = self.AD2pos(element[0], element[1], element[2])
            if point not in self.pointcloud:
                self.pointcloud.append(point)

    def show_sensordata(self):
        self.infomap = self.map.copy()
        for point in self.pointcloud:
            self.infomap.set_at((int(point[0]), int(point[1])), (255, 0, 0))
