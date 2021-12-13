from typing import Tuple
import numpy as np
from .frame import Frame


def distance(
    point: np.ndarray, vertex: np.ndarray
):
    """Computes distance between two points."""
    return np.linalg.norm(point - vertex)


def brute_force(
    a: np.ndarray, v: np.ndarray, t: np.ndarray
) -> np.ndarray:
    """Linearly searches triangles for closest surface triangle."""
    min = np.inf
    closest = 0
    t_index = -1

    for i, tri in enumerate(t):
        p = v[tri[0]]
        q = v[tri[1]]
        r = v[tri[2]]
        A = np.array([q - p, r - p]).T
        B = (a - p).T

        x, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
        x = x.T

        c = p + x[0] * (q - p) + x[1] * (r - p)

        # Check boundaries
        if x[0] < 0:
            c = triangle_bound(c, r, p)
        elif x[1] < 0:
            c = triangle_bound(c, p, q)
        elif (x[0] + x[1]) > 1:
            c = triangle_bound(c, q, r)

        dist = distance(a, c)
        if min > dist:
            min = dist
            closest = c
            t_index = i

    return closest, t_index


def triangle_bound(c, p, q):
    """Computes point projected on triangle edge."""
    l = np.dot((c - p), (q - p)) / np.dot((q - p), (q - p))
    l_s = max(0, min(l, 1))

    return (np.cross((p + l_s), (q - p)))


def find_closest(
    point: np.ndarray, vertices: np.ndarray,
    t: np.ndarray
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
    c, i = brute_force(point, vertices, t)
    return distance(point, c), c, i


def trig_area(a, b, c):
    ab = a - b
    ac = a - c
    S = np.cross(ab, ac) / 2
    return S


def barycenter(atlas: np.ndarray, vert: np.ndarray, v: np.ndarray, c_k: np.ndarray, trig: np.ndarray, i: int):
    """Computes closest vertex to point and returns distance.

        Args:
            atlas (np.ndarray): The atlas of mode weights
            vert (np.ndarray): List of vertices to be matched
            v (np.ndarray): Closest point
            c_k (np.ndarray): Current closest point on triangle
            trig (np.ndarray): List of triangle vertex indices
            i (int): Triangle vertex index for this c

        Returns:
            [return]: [write]
        """

    # Identify vertices of triangle c_k belongs to
    tri = trig[i]
    s = vert[tri[0]]
    t = vert[tri[1]]
    u = vert[tri[2]]

    tolerance = .001
    max_iter = 5
    prev_error = 0

    for j in range(max_iter):
        # Compute barycentric coordinates of c_k
        A = trig_area(s, t, u)
        zeta = trig_area(c_k, t, u) / A
        xi = trig_area(c_k, s, t) / A
        psi = 1 - zeta - xi

        # Compute q_mk for this c_k
        q_mk = np.empty([atlas.shape[0], 3])
        for m in range(atlas.shape[0]):
            # Find q values
            q_mk[m] = zeta * atlas[m, tri[0]] + xi * \
                atlas[m, tri[1]] + psi * atlas[m, tri[2]]

        # Solve least squares problem
        l = np.linalg.lstsq(q_mk.T, c_k.T, rcond=1)[0]
        l = l[1:]  # ignore weight for mode 0

        # Update surface mesh model
        for i in range(vert.shape[0]):
            v_0 = atlas[0, i]
            v_m = atlas[1:, i]
            vert[i] = v_0 + np.dot(l, v_m)

        # Update c_k
        dist, c_k, i = find_closest(v, vert, trig)

        # Check if iteration has stalled
        if np.abs(prev_error - dist) < tolerance:
            break
        prev_error = dist

    return dist, c_k, l
