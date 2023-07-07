import pygame
import math


class Envir:
    def __init__(self, dimensions):
        # Colors
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.yellow = (255, 255, 0)

        # map dimensions
        self.height = dimensions[0]
        self.width = dimensions[1]

        # window settings
        pygame.display.set_caption("Diff Drive Robot")
        self.map = pygame.display.set_mode((self.width, self.height))

        # text variables
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.text = self.font.render('default', True, self.white, self.black)
        self.textRect = self.text.get_rect()
        self.textRect.center = (dimensions[1] - 600, dimensions[0] - 100)

        # trail
        self.trail_set = []

    def write_info(self, Vl, Vr, theta):
        txt = "Vl = {} Vr = {} theta = {}".format(int(Vl), int(Vr), int(math.degrees(theta)))
        self.text = self.font.render(txt, True, self.white, self.black)
        self.map.blit(self.text, self.textRect)

    def trail(self, pos):
        for i in range(0, len(self.trail_set) - 1):
            pygame.draw.line(self.map, self.yellow, (self.trail_set[i][0], self.trail_set[i][1]),
                             (self.trail_set[i + 1][0], self.trail_set[i + 1][1]))

        if self.trail_set.__sizeof__() > 3000:
            self.trail_set.pop(0)
        self.trail_set.append(pos)

    # reference frame
    def robot_frame(self, pos, rotation):
        n = 80
        centerx, centery = pos
        x_axis = (centerx + n * math.cos(-rotation), centery + n * math.sin(-rotation))
        y_axis = (centerx + n * math.cos(-rotation + math.pi / 2), centery + n * math.sin(-rotation + math.pi / 2))
        pygame.draw.line(self.map, self.red, (centerx, centery), x_axis, 3)
        pygame.draw.line(self.map, self.green, (centerx, centery), y_axis, 3)


class Robot:
    def __init__(self, startpos, robotImg, width):
        self.m2p = 8000  # meters to pixels
        # robot_dimensions
        self.w = width
        self.x = startpos[0]
        self.y = startpos[1]
        self.theta = 0

        # Speed
        self.vl = 0.01 * self.m2p  # left velocity
        self.vr = 0.01 * self.m2p  # right velocity
        self.maxspeed = 0.02 * self.m2p
        self.minspeed = -0.02 * self.m2p

        # graphics
        self.img = pygame.image.load(robotImg)
        self.rotated = self.img
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

    def draw(self, map):
        map.blit(self.rotated, self.rect)

    def move(self, event=None):

        if event is not None:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # accelerate
                    self.vl += 0.001 * self.m2p

                elif event.key == pygame.K_a:
                    self.vl -= 0.001 * self.m2p

                elif event.key == pygame.K_e:
                    self.vr += 0.001 * self.m2p

                elif event.key == pygame.K_d:
                    self.vr -= 0.001 * self.m2p

        self.x += ((self.vl + self.vr) / 2) * math.cos(self.theta) * dt
        self.y += ((self.vl + self.vr) / 2) * math.sin(self.theta) * dt
        self.theta += (self.vr - self.vl) / self.w * dt

        # reset theta
        if self.theta > 2 * math.pi or self.theta < -2 * math.pi:
            self.theta = 0

        # set max speed
        self.vr = min(self.vr, self.maxspeed)
        self.vl = min(self.vl, self.maxspeed)

        # set max speed
        self.vr = max(self.vr, self.minspeed)
        self.vl = max(self.vl, self.minspeed)

        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))


# Init
pygame.init()

# Start position
start = (150, 200)

# Dimensions
dims = [600, 1200]

running = True
dt = 0
lasttime = pygame.time.get_ticks()

# Environment
environment = Envir(dims)

# Robot
robot = Robot(start, r"images\red.png", 0.01 * 8000)

FRAMERATE = 25
# simulation loop
clock = pygame.time.Clock()
while running:
    clock.tick(FRAMERATE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # pygame.quit()

        robot.move(event)

    dt = (pygame.time.get_ticks() - lasttime) / 1000
    lasttime = pygame.time.get_ticks()
    pygame.display.update()
    clock.tick(FRAMERATE)

    environment.map.fill(environment.black)

    robot.move()
    environment.write_info(int(robot.vl), int(robot.vr), robot.theta)

    robot.draw(environment.map)
    environment.robot_frame((robot.x, robot.y), robot.theta)
    environment.trail((robot.x, robot.y))
