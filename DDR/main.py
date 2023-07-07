import math
import pygame

from Obstacle_Avoidance import Graphics, Robot, Ultrasonic

map_dim = (600, 1200)

# environment
gfx = Graphics(map_dim, r"images\DDR.png",
               r"images\map.png")

start = (200, 200)
robot = Robot(start, 0.01*3779.52)

# sensor
sensor_range = 250, math.radians(45)
ultra_sonic = Ultrasonic(sensor_range, gfx.map)

dt = 0
last_time = pygame.time.get_ticks()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = (pygame.time.get_ticks() - last_time) / 1000
    last_time = pygame .time.get_ticks()

    gfx.map.blit(gfx.map_img, (0, 0))

    robot.kinematics(dt)
    gfx.draw_robot(robot.x, robot.y, robot.theta)
    point_cloud = ultra_sonic.sense_obstacles(robot.x, robot.y, robot.theta)

    robot.avoid_obstacles(point_cloud, dt)
    gfx.draw_sensor_data(point_cloud)

    pygame.display.update()
