import math

import numpy as np


def compute_normal(tangent):
    # Compute the normal vector given a tangent vector
    normal = np.array([-tangent[1], tangent[0]])  # Rotate 90 degrees
    normal /= np.linalg.norm(normal)  # Normalize the vector
    return normal


# Function to compute the intersection of two lines (2D)
def compute_intersection(p1, p2, p3, p4):
    # Returns the intersection point of two lines defined by points (p1, p2) and (p3, p4)
    a1 = p2[1] - p1[1]
    b1 = p1[0] - p2[0]
    c1 = a1 * p1[0] + b1 * p1[1]

    a2 = p4[1] - p3[1]
    b2 = p3[0] - p4[0]
    c2 = a2 * p3[0] + b2 * p3[1]

    determinant = a1 * b2 - a2 * b1
    if abs(determinant) < 1e-10:
        return None  # Parallel lines
    else:
        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant
        return np.array([x, y])


# Function to evaluate a Bézier curve at parameter t using De Casteljau's algorithm
def evaluate_bezier_curve(curve, t):
    points = [curve["start"]] + curve["controls"] + [curve["end"]]
    n = len(points) - 1  # Degree of the curve
    temp_points = points.copy()

    for r in range(n):
        for i in range(n - r):
            temp_points[i] = (1 - t) * temp_points[i] + t * temp_points[i + 1]

    return temp_points[0]


# Function to evaluate the derivative of a Bézier curve at parameter t
def evaluate_bezier_derivative(curve, t):
    points = [curve["start"]] + curve["controls"] + [curve["end"]]
    n = len(points) - 1  # Degree of the curve

    derivative_points = [(n * (points[i + 1] - points[i])) for i in range(n)]

    temp_points = derivative_points.copy()
    n_derivative = n - 1

    for r in range(n_derivative):
        for i in range(n_derivative - r):
            temp_points[i] = (1 - t) * temp_points[i] + t * temp_points[i + 1]

    return temp_points[0]


# Helper function to determine the number of sampling points based on curve length
def determine_num_points(length, factor=6):
    # Multiply the distance by the factor and ensure a minimum of 100 points
    return max([200, int(length * factor)])


def distance_between_points(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


# Function to offset a Bézier curve of any degree
def offset_bezier_curve(curve, offset, num_points):
    curve = {
        "start": np.array(curve['p1']),
        "controls": [np.array(curve['b1']), np.array(curve['b2'])],
        "end": np.array(curve['p2'])
    }

    # # Calculate the distance from start to end of the curve
    # distance = distance_between_points(curve["start"], curve["end"])
    #
    # # Determine the number of points based on the distance
    # num_points = determine_num_points(distance)

    t_values = np.linspace(0, 1, num_points)
    offset_points = []

    for t in t_values:
        # Compute the point on the curve
        point = evaluate_bezier_curve(curve, t)

        # Compute the derivative at t (tangent vector)
        derivative = evaluate_bezier_derivative(curve, t)

        # Compute normal vector
        normal = compute_normal(derivative)

        # Offset the point
        offset_point = point + normal * offset
        offset_points.append(offset_point)

    return offset_points
