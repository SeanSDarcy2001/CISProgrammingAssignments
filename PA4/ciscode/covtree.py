import numpy as np
from .TriangleThing import TriangleThing
import frame


class CovTreeNode:

    # F: frame
    # UB: np.ndarray
    # LB: np.ndarray
    # HaveSubtrees: int
    # nThings: int

    # WRONG ARGUMENTS?
    # def __init__(self, F: frame, uB: np.ndarray, lB: np.ndarray, HaveSubtrees: int, nThings: int) -> None:
    #     # Define splitting point
    #     self.F = F
    #     self.UB = np.array(uB)
    #     self.LB = np.array(lB)

    #     self.HaveSubtrees: int
    #     self.nThings: int

    # CLASS OUTLINE: DONT NEED IN PYTHON
    # class CovTreeNode {
    #     Frame F
    #     // splitting point
    #     Vec3 UB
    #     Vec3 LB

    #     int HaveSubtrees
    #     self.nThings = nT

    #     CovTreeNode * SubTrees[2]
    #     Thing ** Things
    #     CovTreeNode(Thing ** Ts, int nT)
    #     ConstructSubtrees()
    #     void FindClosestPoint(Vec3 v, double & bound, Vec3 & closest)
    # }

    def __init__(self, Ts: TriangleThing, nT: int) -> None:
        self.Things = Ts
        self.nThings = nT

        self.F = self.ComputeCovFrame(self.Things, self.nThings)
        self.UB, self.LB = self.FindBoundingBox(
            self.F, self.Things, self.nThings)
        self.ConstructSubtrees()

    def ComputeCovFrame(self, Ts: TriangleThing, nT: int):
        Points, nP = ExtractPoints(Ts, nT)
        # May extract nT sort points or perhaps
        # all corner points if things are triangles.
        return self.FindCovFrame(Points, nP)

    def getCentroid(Ps: np.ndarray, nP: int):
        """Returns centroid of a series of points."""
        x = np.sum(Ps[0])
        y = np.sum(Ps[1])
        z = np.sum(Ps[2])
        return np.array([x/nP, y/nP, z/nP])

    def getRotMat(A: np.ndarray):
        """Returns rotation matrix from A matrix."""
        pass

    def FindCovFrame(self, Ps: np.ndarray, nP: int):
        C = self.getCentroid(Ps, nP)

        A = 0
        for i in range(nP):
            A += np.outer(Ps[i], Ps[i])
        R = self.getRotMat(A)

        return frame.Frame(R, C)

    def FindBoundingBox(self, F: frame.Frame, Things: TriangleThing, nThings: int):
        UB = F.inv @ (Things[0].sortPoint())
        LB = F.inv @ (Things[0].sortPoint())

        for k in range(nThings):
            LB, UB = Things[k].enlargeBounds(F, LB, UB)

        return [UB, LB]

    def SplitSort(F: frame.Frame, Ts: TriangleThing, nT: int):
        """find an integer nSplit and reorder Things(...) so that
        F.inverse()*(Thing[k]->SortPoint()).x <0 if and only if k<nSplit.
        This can be done “in place” by suitable exchanges."""
        # TODO: implement
        return 0  # nSplit

    def ConstructSubtrees(self):
        if (self.nThings <= minCount or length(UB-LB) <= minDiag):
            self.HaveSubtrees = 0
            return

        self.HaveSubtrees = 1
        nSplit = self.SplitSort(self.F, self.Things)
        Subtrees_0 = self.CovarianceTreeNode(self.Things[0], nSplit)
        Subtrees_1 = self.CovarianceTreeNode(
            self.Things[nSplit], self.nThings - nSplit)
