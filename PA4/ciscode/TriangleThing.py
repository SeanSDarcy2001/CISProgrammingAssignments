import numpy as np
import frame

class TriangleThing :

    corners : np.ndarray

    #initialize triangle thing with corners 
    def __init__(self, corners: np.ndarray) -> None:
        self.corners = corners

    #returns point that can be used to sort the object
    def sortPoint(self) -> np.ndarray :
        return np.mean(self.corners)
    
    #given a frame F, and corners LB and UB of bounding box around some other things
    #returns the corners of a bounding box that includes Thing2
    def enlargeBounds(self, F: frame, LB: np.ndarray, UB: np.ndarray) -> np.ndarray:
        FiC = F.inv() @ self.corners
        for i in range(3) :
            #x
            LB[0] = np.min(LB[0], FiC[i][0])
            UB[0] = np.max(UB[0], FiC[i][0])
            #y
            LB[1] = np.min(LB[1], FiC[i][1])
            UB[1] = np.max(UB[1], FiC[i][1])
            #z
            LB[2] = np.min(LB[2], FiC[i][2])
            UB[2] = np.max(UB[2], FiC[i][2])
        return np.ndarray([LB, UB])


    def boundingBox(self, F: frame) -> np.ndarray :
        return self.enlargeBounds(F, np.ndarray(np.Inf, np.Inf, np.Inf), np.ndarray(np.NINF, np.NINF, np.NINF))

    #returns 1 if any part of FiC in bounding box with corners LB and UB
    def mayBeInBounds(self, F: frame, LB: np.ndarray, UB: np.ndarray) -> int :
        FiC = F.inv() @ self.corners
        for i in range(3) :
             if self.inBounds(FiC[i], LB, UB) :
                return 1
        return 0

    ##TODO Implement
    def inBounds(self, F: frame, LB: np.ndarray, UB: np.ndarray) -> bool :
        return NotImplementedError