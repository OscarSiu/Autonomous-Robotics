import env
import features
import sensor
import random
import pygame


def random_color():
    levels = range(32, 256, 32)
    return tuple(random.choice(levels) for _ in range(3))


Feature_map = features.featureDetection()
environment = env.build_env((600, 1200))
originalMap = environment.map.copy()
laser = sensor.LaserSensor(200, originalMap, uncertainty=(0.5, 0.01))
environment.map.fill((255, 255, 255))
environment.infomap = environment.map.copy()
originalMap = environment.map.copy()

running = True
FEATURE_DETECTION = True
breakpoint_ind = 0

while running:
    environment.infomap = originalMap.copy()
    FEATURE_DETECTION = True
    breakpoint_ind = 0
    endpoints = [0, 0]
    sensorson = False
    predicted_pts2draw = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_focused():
        sensorson = True

    elif not pygame.mouse.get_focused():
        sensorson = False

    if sensorson:
        position = pygame.mouse.get_pos()
        laser.pos = position
        sensor_data = laser.sense_obs()
        Feature_map.laser_points_set(sensor_data)

        while breakpoint_ind < (Feature_map.NP - Feature_map.pmin):
            seedSeg = Feature_map.seed_segment_detection(laser.pos, breakpoint_ind)
            if not seedSeg:
                break

            else:
                seedSegment = seedSeg[0]
                predicted_pts2draw = seedSeg[1]
                indices = seedSeg[2]
                results = Feature_map.seed_segment_growing(indices, breakpoint_ind)
                if not results:
                    breakpoint_ind = indices[1]
                    continue

                else:
                    line_eq = results[1]
                    m, c = results[5]
                    line_seg = results[0]
                    outermost = results[2]
                    breakpoint_ind = results[3]

                    endpoints[0] = Feature_map.projection_pt2line(outermost[0], m, c)
                    endpoints[1] = Feature_map.projection_pt2line(outermost[1], m, c)
                    Feature_map.features.append([[m, c], endpoints])

                    color = (255, 0, 0)

                    for point in line_seg:
                        environment.infomap.set_at((int(point[0][0]), int(point[0][1])), (0, 255, 0))
                        pygame.draw.circle(environment.infomap, color, (int(point[0][0]), int(point[0][1])), 2, 0)
                    pygame.draw.line(environment.infomap, (0, 255, 0), endpoints[0], endpoints[1], 2)

                    environment.dataStorage(sensor_data)

                    Feature_map.features = Feature_map.linefeats2pts()
                    features.landmark_association(Feature_map.features)

        for landmark in features.Landmarks:
            pygame.draw.line(environment.infomap, (0, 0, 255), landmark[1][0], landmark[1][1], 2)

    environment.map.blit(environment.infomap, (0, 0))
    pygame.display.update()
