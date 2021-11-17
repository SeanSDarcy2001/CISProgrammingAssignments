from typing import Tuple
import numpy as np
from .frame import Frame


def distance(
    point: np.ndarray, vertex: np.ndarray
) -> np.float64:
    return np.linalg.norm(point - vertex)


def brute_force(
    a: np.ndarray, v: np.ndarray, t: np.ndarray
) -> np.ndarray:
    min = np.inf
    closest = 0

    for i, tri in enumerate(t):
        p = v[tri[0]]
        q = v[tri[1]]
        r = v[tri[2]]
        A = np.array([q - p, r - p]).T
        B = (a - p).T

        x, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        x = x.T

        c = p + x[0] * (q - p) + x[1] * (r - p)

        dist = distance(a, c)
        if min > dist:
            min = dist
            closest = c

    return closest


def get_closest_vertex(
    point: np.ndarray, vertices: np.ndarray,
    t: np.ndarray, brute: bool = True
) -> Tuple[np.float64, np.ndarray]:
    """Computes closest vertex to point and returns distance.

    Args:
        points (np.ndarray): The point of interest
        vertices (np.ndarray): List of vertices to be matched
        t (np.ndarray): List of triangle vertex indices
        brute (bool): Whether or not to use brute-force search

    Returns:
        Tuple[np.float32, np.ndarray]: The distance between the closest
            two points, and the location of the closest vertex in CT
            coordinates.
    """
    if brute:
        c = brute_force(point, vertices, t)
        return distance(point, c), c
    else:
        c = brute_force(point, vertices, t)
        return distance(point, c), c
