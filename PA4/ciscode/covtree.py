import numpy as np
from .TriangleThing import TriangleThing
from .frame import Frame


class CovTreeNode:

    def __init__(self, Ts: list, nT: int):
        self.Things = Ts
        self.nThings = nT

        self.F = self.ComputeCovFrame()
        self.UB, self.LB = self.FindBoundingBox()
        self.ConstructSubtrees()

    def appInvFrame(F: Frame, T: TriangleThing):
        return F.inv @ T.sortPoint()

    def extractPoints(Ts: np.ndarray, nT: int) -> np.ndarray:
        """Return sort points for Thing."""
        sort_points = np.empty((nT, 3))
        for i in range(nT):
            sort_points[i] = Ts[i].sortPoint()
        return sort_points

    def ComputeCovFrame(self):
        """Extract sort points of all Things to compute covariance frame."""
        Ts = self.Things
        nT = self.nThings
        Points, nP = self.extractPoints(Ts, nT)
        return self.FindCovFrame(Points, nP)

    def getCentroid(Ps: np.ndarray, nP: int):
        """Returns centroid of a series of points."""
        x = np.sum(Ps[0])
        y = np.sum(Ps[1])
        z = np.sum(Ps[2])
        return np.array([x/nP, y/nP, z/nP])

    def getRotMat(A: np.ndarray):
        """Returns rotation matrix from A matrix."""
        l, Q = np.linalg.eig(A)
        qi = np.argmax(l)
        q = Q[:, qi]
        R = np.array([[q[0]**2 + q[1]**2 - q[2]**2 - q[3]**2,
                       2*(q[1]*q[2] - q[0]*q[3]),
                       2*(q[1]*q[3] + q[0]*q[2])],

                      [2*(q[1]*q[2] + q[0]*q[3]),
                       q[0]**2 - q[1]**2 + q[2]**2 - q[3]**2,
                       2*(q[2]*q[3] - q[0]*q[1])],

                      [2*(q[1]*q[3] - q[0]*q[2]),
                       2*(q[2]*q[3] + q[0]*q[1]),
                       q[0]**2 - q[1]**2 - q[2]**2 + q[3]**2]])

    def FindCovFrame(self, Ps: np.ndarray, nP: int):
        """Find covariance frame by finding centroid and rotation."""
        C = self.getCentroid(Ps, nP)

        A = 0
        for i in range(nP):
            A += np.outer(Ps[i], Ps[i])
        R = self.getRotMat(A)

        return Frame(R, C)

    def FindBoundingBox(self):
        """Find bounding box encompassing a list of Things."""
        F = self.F
        Things = self.Things
        nThings = self.nThings

        UB = self.appInvFrame(F, Things[0])
        LB = self.appInvFrame(F, Things[0])

        for k in range(nThings):
            LB, UB = Things[k].enlargeBounds(F, LB, UB)

        return [UB, LB]

    def partition(self, arr, low, high):
        """Returns pivot index for quicksort."""
        i = (low-1)
        pivot = self.appInvFrame(self.F, arr[high])[0]

        for j in range(low, high):

            # If current element is smaller than or
            # equal to pivot
            if self.appInvFrame(self.F, arr[j])[0] <= pivot:

                # increment index of smaller element
                i = i+1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i+1], arr[high] = arr[high], arr[i+1]
        return (i+1)

    def quickSort(self, arr, low, high):
        """Function to perform quicksort."""
        if len(arr) == 1:
            return arr
        if low < high:
            # pi is partitioning index, arr[p] is now
            # at right place
            p = self.partition(arr, low, high)

            # Separately sort elements before
            # partition and after pivot
            self.quickSort(arr, low, p-1)
            self.quickSort(arr, p+1, high)

    def SplitSort(self):
        """Find nSplit and reorder Things so that
        F.inverse() @ (Thing[k]->SortPoint()).x < 0 iff k < nSplit."""
        # This can be done in place by suitable exchanges
        F = self.F
        Ts = self.Things
        nT = self.nThings

        self.Things = self.quickSort(Ts, 0, nT-1)
        for i in range(nT):
            if (self.appInvFrame(F, self.Things[i])[0] >= 0):
                return i

        return nT

    def ConstructSubtrees(self, minCount, minDiag):
        if (self.nThings <= minCount or np.linalg.norm(self.UB-self.LB) <= minDiag):
            self.HaveSubtrees = 0
            return

        self.HaveSubtrees = 1
        nSplit = self.SplitSort(self.F, self.Things)
        self.lSubtree = self.CovarianceTreeNode(self.Things[0], nSplit)
        self.rSubtree = self.CovarianceTreeNode(
            self.Things[nSplit], self.nThings - nSplit)

    def findClosestPoint(self, v: np.ndarray, bound: np.float64):
        closest = np.empty(3)
        # Transform v to local coordinate system
        vLocal = self.F.inv @ v
        if vLocal[0] > self.UB[0]+bound:
            return
        if vLocal[1] > self.UB[1]+bound:
            return
        # similar checks on remaining bounds go here ....;
        if vLocal[2] > self.UB[2]+bound:
            return
        if self.HaveSubtrees:
            self.lSubtree.FindClosestPoint(v, bound, closest)
            self.rSubtree.FindClosestPoint(v, bound, closest)
        else:
            for i in range(self.nThings):
                closest = self.UpdateClosest(self.Things[i], v, bound)

        return closest

    def UpdateClosest(self, T: TriangleThing, v: np.ndarray, bound: np.float64) -> np.ndarray:
        cp = T.closestPointTo(v)
        dist = np.linalg.norm(cp-v)
        if (dist < bound):
            bound = dist
            return cp
        return np.empty(3)
