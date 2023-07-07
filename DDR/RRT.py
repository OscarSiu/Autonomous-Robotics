import pygame
from RRTBase import RRTMap
from RRTBase import RRTGraph
import time

def main():
    dimensions = (650, 1000)
    start = (50, 50)
    goal = (800, 500)
    obsdim = 30
    obsnum = 50

    iterations = 0
    t1 = 0
    pygame.init()
    map = RRTMap(start, goal, dimensions, obsdim, obsnum)
    graph = RRTGraph(start, goal, dimensions, obsdim, obsnum)

    obstacles = graph.makeobs()

    map.drawMap(obstacles)
    t1 = time.time()
    while not graph.path_to_goal():
        elapsed = time.time() - t1
        t1 = time.time()
        if elapsed > 30:
            raise

        if iterations % 10 == 0:
            X, Y, Parent = graph.bias(goal)
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad + 2, map.nodeThickness)
            pygame.draw.line(map.map, map.blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]), map.edgeThickness)
        else:
            X, Y, Parent = graph.expand()
            pygame.draw.circle(map.map, map.grey, (X[-1], Y[-1]), map.nodeRad + 2, map.nodeThickness)
            pygame.draw.line(map.map, map.blue, (X[-1], Y[-1]), (X[Parent[-1]], Y[Parent[-1]]), map.edgeThickness)

        if iterations % 10 == 0:
            pygame.display.update()

        iterations += 1

    map.drawPath(graph.getPathCoords())
    pygame.display.update()
    pygame.event.clear()
    pygame.event.wait()


'''
        x, y = graph.sample_envir()
        n = graph.num_of_nodes()
        graph.add_node(n, x, y)
        graph.add_edge(n - 1, n)
        x1, y1 = graph.x[n], graph.y[n]
        x2, y2 = graph.x[n - 1], graph.y[n - 1]
        if graph.isFree():
            pygame.draw.circle(map.map, map.red, (graph.x[n], graph.y[n]), map.nodeRad, map.nodeThickness)
            if not graph.crossObstacle(x1, x2, y1, y2):
                pygame.draw.line(map.map, map.blue, (x1, y1), (x2, y2), map.edgeThickness)

        pygame.display.update()
'''

if __name__ == '__main__':
    result = False
    while not result:
        try:
            main()
            result = True
        except:
            result = False

'''
class robot:
    def move(self, dt, event=None):
        self.x += (self.u * math.cos(self.theta) - self.a * math.sin(self.theta) * self.W) * dt
        self.y += (self.u * math.sin(self.theta) + self.a * math.cos(self.theta) * self.W) * dt
        self.theta += self.W * dt

        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(-self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))
        self.follow_path()

    def follow_path(self):
        target = self.path[self.waypoint]
        delta_x = target[0] - self.x
        delta_y = target[1] - self.y
        self.u = delta_x * math.cos(self.theta) + delta_y * math.sin(self.theta)
        self.W = (-1 / self.a) * math.sin(self.theta) * delta_x + (1 / self.a) * math.cos(self.theta) * delta_y
        if self.dist((self.x, self.y), self.path[self.waypoint]) <= 35:
            self.waypoint -= 1
        if self.waypoint <= 0:
            self.waypoint = 0
'''
