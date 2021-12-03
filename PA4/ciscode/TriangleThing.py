import numpy as np
from ciscode import frame, closest


class TriangleThing:

    def __init__(self, corners: np.ndarray) -> None:
        """Initialize triangle thing using triangle vertices."""
        self.corners = corners

    def sortPoint(self) -> np.ndarray:
        """Returns point that can be used to sort the object."""
        return np.mean(self.corners, axis=0)

    def enlargeBounds(self, F: frame, LB: np.ndarray, UB: np.ndarray) -> np.ndarray:
        """Given a frame F, and corners LB and UB of bounding box
        around some other things, returns the corners of a bounding
        box that includes Thing2."""
        FiC = F.inv() @ self.corners
        for i in range(3):
            # x
            LB[0] = np.min(LB[0], FiC[i][0])
            UB[0] = np.max(UB[0], FiC[i][0])
            # y
            LB[1] = np.min(LB[1], FiC[i][1])
            UB[1] = np.max(UB[1], FiC[i][1])
            # z
            LB[2] = np.min(LB[2], FiC[i][2])
            UB[2] = np.max(UB[2], FiC[i][2])
        return np.ndarray([LB, UB])

    def boundingBox(self, F: frame) -> np.ndarray:
        return self.enlargeBounds(F, np.ndarray(np.Inf, np.Inf, np.Inf), np.ndarray(np.NINF, np.NINF, np.NINF))

    def mayBeInBounds(self, F: frame, LB: np.ndarray, UB: np.ndarray) -> int:
        """Returns 1 if any part of FiC in bounding box with corners LB and UB."""
        FiC = F.inv() @ self.corners
        for i in range(3):
            if self.inBounds(FiC[i], LB[i], UB[i]):
                return 1
        return 0

    def inBounds(n: int, LB: int, UB: int) -> bool:
        """Returns true if a given frame Finv * this is in bounds of box
        given by LB and UB."""
        top = np.max(LB, UB)
        bot = np.min(LB, UB)
        return n >= bot and n <= top

    def closestPointTo(self, v: np.ndarray):
        """Find closest point to given vector."""
        max_point = 0
        min_dist = np.inf
        for i in range(3):
            point = self.corners[i]
            if (closest.distance(point, v) < min_dist):
                max_point = point
        return point
