from typing import Tuple
import numpy as np
from .frame import Frame


def distance(
    point: np.ndarray, vertex: np.ndarray
) -> np.float64:
    return np.linalg.norm(point - vertex)


def brute_force(
    point: np.ndarray, vertices: np.ndarray
) -> np.ndarray:
    min = np.inf
    index = -1
    for i, v in enumerate(vertices):
        dist = distance(point, v)
        if min > dist:
            min = dist
            index = i

    # return vertices.argmin(distance(point, vertices), axis=0)
    return index


def get_closest_vertex(
    point: np.ndarray, vertices: np.ndarray, brute: bool = True
) -> Tuple[np.float64, np.ndarray]:
    """Computes closest vertex to point and returns distance.

    Args:
        points (np.ndarray): The point of interest
        vertices (np.ndarray): List of vertices to be matched
        brute (bool): Whether or not to use brute-force search

    Returns:
        Tuple[np.float32, np.ndarray]: The distance between the closest
            two points, and the location of the closest vertex in CT
            coordinates.
    """
    if brute:
        i = brute_force(point, vertices)
        return distance(point, vertices[i]), vertices[i]
    else:
        i = brute_force(point, vertices)
        return distance(point, vertices[i]), vertices[i]
