import env, sensor
import pygame
import math

environment = env.build_env((600, 1200))
environment.originalMap = environment.map.copy()
laser = sensor.LaserSensor(200, environment.originalMap, uncertainty=(0.5, 0.01))
environment.map.fill((0, 0, 0))
environment.infomap = environment.map.copy()

running = True

while running:
    sensorON = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if pygame.mouse.get_focused():
            sensorON = True

        elif not pygame.mouse.get_focused():
            sensorON = False

    if sensorON:
        position = pygame.mouse.get_pos()
        laser.pos = position
        sensor_data = laser.sense_obs()
        environment.dataStorage(sensor_data)
        environment.show_sensordata()

    environment.map.blit(environment.infomap, (0, 0))
    pygame.display.update()

    pygame.display.update()
