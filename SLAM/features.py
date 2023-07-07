import numpy as np
import math
from fractions import Fraction
from scipy.odr import *

Landmarks = []


class featureDetection:
    def __init__(self):
        # variables
        self.epsilon = 10
        self.delta = 501  # delta ==20 for less noise
        self.snum = 6
        self.pmin = 20
        self.gmax = 20
        self.seed_segments = []
        self.line_segments = []
        self.laserpoints = []
        self.line_params = None
        self.NP = len(self.laserpoints) - 1
        self.lmin = 20  # min length of a line segment
        self.LR = 0  # real length
        self.PR = 0  # num of laser points contained in the line segments
        self.two_points = []
        self.features = []

    # euclidean distance from pt1 to pt2
    @staticmethod
    def dis_pt2pt(point1, point2):
        px = (point1[0] - point2[0]) ** 2
        py = (point1[1] - point2[1]) ** 2
        return math.sqrt(px + py)

    # distance point to line in general form
    def dist_pt2line(self, params, point):
        a, b, c = params
        distance = abs(a * point[0] + b * point[1] + c) / math.sqrt(a ** 2 + b ** 2)
        return distance

    #  extract 2 points from line equation under slope intercepts form
    def line_2pts(self, m, b):
        x = 5
        y = m * x + b
        x2 = 2000
        y2 = m * x2 + b
        return [(x, y), (x2, y2)]

    # general form to slope-intercept
    def lineForm_G2SI(self, a, b, c):
        m = -a / b
        b = -c / b
        return m, b

    # slope-intercept to general form
    def lineForm_SI2G(self, m, b):
        a, b, c = -m, 1, -b
        if a < 0:
            a, b, c = -a, -b, -c

        den_a = float(Fraction(a).limit_denominator(1000)).as_integer_ratio()[1]
        den_c = float(Fraction(c).limit_denominator(1000)).as_integer_ratio()[1]
        gcd = np.gcd(den_a, den_c)
        lcm = den_a * den_c / gcd

        a = a * lcm
        b = b * lcm
        c = c * lcm
        return a, b, c

    def line_intersect_general(self, params1, params2):
        a1, b1, c1 = params1
        a2, b2, c2 = params2
        x = (c1 * b2 - b1 * c2) / (b1 * a2 - a1 * b2)
        y = (a1 * c2 - a2 * c1) / (b1 * a2 - a1 * b2)
        return x, y

    def pts_2line(self, point1, point2):
        m, b = 0, 0
        if point2[0] == point1[0]:
            pass
        else:
            m = (point2[1] - point1[1]) / (point2[0] - point1[0])
            b = point2[1] - m * point2[0]
        return m, b

    def projection_pt2line(self, point, m, b):
        x, y = point
        m2 = -1 / m
        c2 = y - m2 * x
        intersection_x = -(b - c2) / (m - m2)
        intersection_y = m2 * intersection_x + c2
        return intersection_x, intersection_y

    def AD2pos(self, distance, angle, robot_pos):
        x = distance * math.cos(angle) + robot_pos[0]
        y = -distance * math.sin(angle) + robot_pos[1]
        return (int(x), int(y))

    def laser_points_set(self, data):
        self.laserpoints = []
        if not data:
            pass

        else:
            for point in data:
                coordinates = self.AD2pos(point[0], point[1], point[2])
                self.laserpoints.append([coordinates, point[1]])
        self.NP = len(self.laserpoints) - 1

    # define a quadratic function to fit the data
    def linear_func(self, p, x):
        m, b = p
        return m * x + b

    # orthogonal distance regression
    def odr_fit(self, laser_points):
        x = np.array([i[0][0] for i in laser_points])
        y = np.array([i[0][1] for i in laser_points])

        # Create model for fitting
        linear_model = Model(self.linear_func)

        # Create a real data object using initiated data
        data = RealData(x, y)

        # Set ODR with model and data
        odr_model = ODR(data, linear_model, beta0=[0., 0.])

        # Run regression
        out = odr_model.run()
        m, b = out.beta
        return m, b

    def predictpt(self, line_params, sensed_pt, robotpos):
        m, b = self.pts_2line(robotpos, sensed_pt)
        params1 = self.lineForm_SI2G(m, b)
        predx, predy = self.line_intersect_general(params1, line_params)
        return predx, predy

    def seed_segment_detection(self, robot_pos, breakpoint_ind):
        flag = True
        self.NP = max(0, self.NP)
        self.seed_segments = []
        for i in range(breakpoint_ind, (self.NP - self.pmin)):
            predicted_pts_to_draw = []
            j = i + self.snum
            m, c = self.odr_fit(self.laserpoints[i:j])

            params = self.lineForm_SI2G(m, c)

            for k in range(i, j):
                predicted_point = self.predictpt(params, self.laserpoints[k][0], robot_pos)
                predicted_pts_to_draw.append(predicted_point)
                d1 = self.dis_pt2pt(predicted_point, self.laserpoints[k][0])

                if d1 > self.delta:
                    flag = False
                    break
                d2 = self.dist_pt2line(params, self.laserpoints[k][0])

                if d2 > self.epsilon:
                    flag = False
                    break

            if flag:
                self.line_params = params
                return [self.laserpoints[i:j], predicted_pts_to_draw, (i, j)]
        return False

    def seed_segment_growing(self, indices, breakpoint):
        line_eq = self.line_params
        i, j = indices

        # beginning and final points in the line segment
        pb, pf = max(breakpoint, i - 1), min(j + 1, len(self.laserpoints) - 1)

        while self.dist_pt2line(line_eq, self.laserpoints[pf][0]) < self.epsilon:
            if pf > self.NP - 1:
                break
            else:
                m, b = self.odr_fit(self.laserpoints[pb:pf])
                line_eq = self.lineForm_SI2G(m, b)

                point = self.laserpoints[pf][0]

            pf = pf + 1
            nextpoint = self.laserpoints[pf][0]
            if self.dis_pt2pt(point, nextpoint) > self.gmax:
                break

        pf = pf - 1

        while self.dist_pt2line(line_eq, self.laserpoints[pb][0]) < self.epsilon:
            if pb < breakpoint:
                break
            else:
                m, b = self.odr_fit(self.laserpoints[pb:pf])
                line_eq = self.lineForm_SI2G(m, b)

                point = self.laserpoints[pb][0]

            pb = pb - 1
            nextpoint = self.laserpoints[pb][0]
            if self.dis_pt2pt(point, nextpoint) > self.gmax:
                break

        pb = pb + 1

        lr = self.dis_pt2pt(self.laserpoints[pb][0], self.laserpoints[pf][0])
        pr = len(self.laserpoints[pb:pf])

        if (lr >= self.lmin) and (pr >= self.pmin):
            self.line_params = line_eq
            m, b = self.lineForm_G2SI(line_eq[0], line_eq[1], line_eq[2])
            self.two_points = self.line_2pts(m, b)
            self.line_segments.append((self.laserpoints[pb + 1][0], self.laserpoints[pf - 1][0]))
            return [self.laserpoints[pb:pf], self.two_points,
                    (self.laserpoints[pb + 1][0], self.laserpoints[pf - 1][0]), pf, line_eq, (m, b)]

        else:
            return False

    def linefeats2pts(self):
        new_rep = []

        for feature in self.features:
            projection = self.projection_pt2line((0, 0), feature[0][0], feature[0][1])
            new_rep.append([feature[0], feature[1], projection])

        return new_rep


def landmark_association(landmarks):
    threshold = 10
    for l in landmarks:
        flag = False
        for i, landmark in enumerate(Landmarks):
            dist = featureDetection.dis_pt2pt(l[2], landmark[2])
            if dist < threshold:
                if not is_overlap(l[1], landmark[1]):
                    continue

                else:
                    Landmarks.pop(i)
                    Landmarks.insert(i, l)
                    flag = True

                    break
        if not flag:
            Landmarks.append(l)


def is_overlap(seg1, seg2):
    len1 = featureDetection.dis_pt2pt(seg1[0], seg1[1])
    len2 = featureDetection.dis_pt2pt(seg2[0], seg2[1])
    center1 = ((seg1[0][0] + seg1[1][0]) / 2, (seg1[0][1] + seg1[1][1]) / 2)
    center2 = ((seg2[0][0] + seg2[1][0]) / 2, (seg2[0][1] + seg2[1][1]) / 2)

    dist = featureDetection.dis_pt2pt(center1, center2)
    if dist > (len1 + len2) / 2:
        return False
    else:
        return True
