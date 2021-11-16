from __future__ import annotations
from typing import Union
from typing import Type

import numpy as np
import logging

log = logging.getLogger(__name__)


class Frame:
    def __init__(self, r: np.ndarray, p: np.ndarray) -> None:
        """Create a frame with rotation `r` and translation `p`.

        Args:
            r (np.ndarray): Rotation.
            p (np.ndarray): translation.
        """
        self.r = np.array(r)
        self.p = np.array(p)

    def __array__(self):
        out = np.eye(4, dtype=np.float32)
        out[:3, :3] = self.r
        out[:3, 3] = self.p
        return out

    def __str__(self):
        return np.array_str(np.array(self), precision=4, suppress_small=True)

    def inv(self) -> Frame:
        return Frame(self.r.T, -(self.r.T @ self.p))

    def __matmul__(self, other: Union[np.ndarray, Frame]) -> Frame:
        """[summary]

        Args:
            other (Union[np.ndarray, Frame]): [description]

        Returns:
            Frame: [description]
        """

        if isinstance(other, np.ndarray):
            return (self.r @ other.T).T + self.p
        elif isinstance(other, Frame):
            return Frame(self.r @ other.r, self.r @ other.p + self.p)
        else:
            raise TypeError

    @classmethod
    def from_points(cls: Type[Frame], a: np.ndarray, b: np.ndarray) -> Frame:
        """Register the two point clouds with F_BA, where b = F_BA @ a.

        ..

                  ^
                  |
                 A+--->
                  ^
              ^  / F_BA
              | /
            B +--->

        Args:
            cls (Type[Frame]): The class.
            a (np.ndarray): Array of points in frame A.
            b (np.ndarray): Array of corresponding points in frame B.

        Raises:
            RuntimeError: If the points fail to register.

        Returns:
            Frame: The F_BA transform.
        """
        N = a.shape[0]

        # get centroids
        a_m = a.mean(axis=0)
        b_m = b.mean(axis=0)

        # get points in centroid frames
        a_q = a - a_m
        b_q = b - b_m

        # Solve SVD
        H = np.sum([np.outer(a_q[i], b_q[i]) for i in range(N)], axis=0)
        U, S, VT = np.linalg.svd(H)
        V = VT.T
        R = V @ U.T

        d = np.linalg.det(R)
        if d < 0:
            V[:, 2] *= -1
            R = V @ U.T
            d = np.linalg.det(R)

        if not np.isclose(d, 1):
            raise RuntimeError(f"det(R) = {d}, should be +1 for rotation matrices.")

        return Frame(R, b_m - R @ a_m)

    @classmethod
    def from_icp(cls, xs, ys):
        pass

    @classmethod
    def from_surface_registration(cls, points, surface):
        pass
