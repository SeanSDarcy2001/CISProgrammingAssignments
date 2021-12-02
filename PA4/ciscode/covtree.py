import numpy as np
import frame

class CovTreeNode :
    F : frame
    UB : np.ndarray
    LB : np.ndarray
    HaveSubtrees : int
    nThings : int

    def __init__(self, F: frame, uB: np.ndarray, lB: np.ndarray, HaveSubtrees: int, nThings: int) -> None:
        self.F = F
        self.UB = np.array(uB)
        self.LB = np.array(lB)
        self.HaveSubtrees : int
        self.nThings : int


