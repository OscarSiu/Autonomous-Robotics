import pygame
import math


class Robot:
    def __init__(self, startpos, robotimg, width, follow=None):
        self.leader = False
        self.follow = follow

        self.m2p = 8000

        self.x, self.y = startpos
        self.theta = 0
        self.trail_set = []
        self.a = 20
        self.w = width

        # relation velocity
        self.u = 30  # pix/sec
        self.W = 0  # rad/sec

        self.img = pygame.image.load(robotimg)  # skin img path provided in arguments
        self.rotated = self.img
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

    def move(self, event=None):

        self.x += (self.u * math.cos(self.theta) - self.a * math.sin(self.theta) * self.W) * dt
        self.y += (self.u * math.sin(self.theta) + self.a * math.cos(self.theta) * self.W) * dt
        self.theta += self.W*dt

        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(-self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

        if self.leader:
            if event is not None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # accelerate
                        self.u += 0.001 * self.m2p

                    elif event.key == pygame.K_a:
                        self.u -= 0.001 * self.m2p

                    elif event.key == pygame.K_e:
                        self.W += 0.001 * self.m2p

                    elif event.key == pygame.K_d:
                        self.W -= 0.001 * self.m2p
        else:
            self.following()

    def following(self):
        target = self.follow.trail_set[0]
        delta_x = target[0] - self.x
        delta_y = target[1] - self.y
        self.u = delta_x * math.cos(self.theta) + delta_y * math.sin(self.theta)
        self.W = (-1 / self.a) * math.sin(self.theta) * delta_x + (1 / self.a) * math.cos(self.theta) * delta_y

    def dist(self, point1, point2):
        (x1, y1) = point1
        (x2, y2) = point2
        x1 = float(x1)
        x2 = float(x2)
        y1 = float(y1)
        y2 = float(y2)

        px = (x1 - x2) ** 2
        py = (y1 - y2) ** 2
        distance = (px + py) ** 0.5
        return distance

    def draw(self, map):
        map.blit(self.rotated, self.rect)

    def trail(self, pos, map, color):
        for i in range(0, len(self.trail_set) - 1):
            pygame.draw.line(map, color, (self.trail_set[i][0], self.trail_set[i][1]),
                             (self.trail_set[i + 1][0], self.trail_set[i + 1][1]))

        if self.trail_set.__sizeof__() > 2000:
            self.trail_set.pop(0)
        self.trail_set.append(pos)


class Envir:
    def __init__(self, dimensions):
        # colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)

        # map dimensions
        self.height, self.width = dimensions

        # window settings
        pygame.display.set_caption("multi robot sim")
        self.map = pygame.display.set_mode((self.width, self.height))

    def write_info(self):
        pass

    def robot_frame(self):
        pass


def robot_sim(Robot, event=None):
    Robot.move(event=event)
    Robot.draw(environment.map)
    Robot.trail((Robot.x, Robot.y), environment.map, environment.yellow)


# init
pygame.init()
running = True

skins = [r"C:\Users\User\PycharmProjects\DDR\images\DDR.png",
         r"C:\Users\User\PycharmProjects\DDR\images\green.png",
         r"C:\Users\User\PycharmProjects\DDR\images\red.png",
         r"C:\Users\User\PycharmProjects\DDR\images\light_green.png",
         r"C:\Users\User\PycharmProjects\DDR\images\purple.png"]

# Config setup
start = (200, 200)
dims = (600, 1200)

iterations = 0
dt = 0
lasttime = pygame.time.get_ticks()

FRAMERATE = 30
clock = pygame.time.Clock()

# Environment
environment = Envir(dims)

# Robots
# robot = Robot(start, r"C:\Users\User\PycharmProjects\DDR\images\DDR.png", 80, follow=None)
robots_num = 5
robots = []
# leader
robots.append(Robot(start, skins[0], width=80))
robots[0].leader = True
# followers
for i in range(1, robots_num):
    robot = Robot((start[0] - i * 100, start[1]), skins[i], 80, robots[i - 1])
    robots.append(robot)

# Simulation loop
while running:
    clock.tick(FRAMERATE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for robot in robots:
            if not robot.leader and iterations < 1:
                continue
            robot_sim(robot, event)

    for robot in robots:
        if not robot.leader and iterations < 1:
            continue
        robot_sim(robot)

    clock.tick(FRAMERATE)
    pygame.display.update()
    environment.map.fill(environment.black)
    dt = (pygame.time.get_ticks() - lasttime) / 1000  # seconds
    lasttime = pygame.time.get_ticks()
    iterations += 1
