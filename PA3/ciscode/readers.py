import numpy as np
from pathlib import Path


class CalBody:
    """Parses the calibration body data."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "r") as f:
            line = next(f)
            toks = line.replace(" ", "").split(",")
            self.N_D = int(toks[0])
            self.N_A = int(toks[1])
            self.N_C = int(toks[2])

        arr = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
        self.d = arr[: self.N_D]
        self.a = arr[self.N_D : self.N_D + self.N_A]
        self.c = arr[self.N_D + self.N_A :]


class CalReadings:
    """Parses the calibration readings data."""

    def __init__(self, path: str):
        self.path = Path(path)
        with open(path, "r") as f:
            line = next(f)
            toks = line.replace(" ", "").split(",")
            self.N_D = int(toks[0])
            self.N_A = int(toks[1])
            self.N_C = int(toks[2])
            self.N_frames = int(toks[3])

        arr = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
        self.D = np.empty([self.N_frames, self.N_D, 3], np.float64)
        self.A = np.empty([self.N_frames, self.N_A, 3], np.float64)
        self.C = np.empty([self.N_frames, self.N_C, 3], np.float64)
        for f, st in enumerate(range(0, arr.shape[0], self.N_D + self.N_A + self.N_C)):
            self.D[f] = arr[st : st + self.N_D]
            self.A[f] = arr[st + self.N_D : st + self.N_D + self.N_A]
            self.C[f] = arr[
                st + self.N_D + self.N_A : st + self.N_D + self.N_A + self.N_C
            ]


class EMPivot:
    """Parses the EM pivot data."""

    def __init__(self, path):
        self.path = Path(path)
        with open(path, "r") as f:
            line = next(f)
            toks = line.replace(" ", "").split(",")
            self.N_G = int(toks[0])
            self.N_frames = int(toks[1])

        arr = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
        self.G = np.empty([self.N_frames, self.N_G, 3], np.float64)
        for k, st in enumerate(range(0, arr.shape[0], self.N_G)):
            self.G[k] = arr[st : st + self.N_G]


class OptPivot:
    """Parses the optical pivot data."""

    def __init__(self, path):
        self.path = path
        with open(path, "r") as f:
            line = next(f)
            toks = line.replace(" ", "").split(",")
            self.N_D = int(toks[0])
            self.N_H = int(toks[1])
            self.N_frames = int(toks[2])

        arr = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
        self.D = np.empty([self.N_frames, self.N_D, 3], np.float64)
        self.H = np.empty([self.N_frames, self.N_H, 3], np.float64)
        for f, st in enumerate(range(0, arr.shape[0], self.N_D + self.N_H)):
            self.D[f] = arr[st : st + self.N_D]
            self.H[f] = arr[st + self.N_D : st + self.N_D + self.N_H]


class OutputReader:
    """Parses a formatted output file for programming assignment 1."""

    def __init__(self, path):
        self.path = Path(path)
        with open(path, "r") as f:
            line = next(f)
            toks = line.replace(" ", "").split(",")
            self.N_C = int(toks[0])
            self.N_frames = int(toks[1])

        arr = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
        self.em_post = arr[0]
        self.opt_post = arr[1]
        arr = arr[2:]
        self.C = np.empty([self.N_frames, self.N_C, 3], np.float64)
        for f, st in enumerate(range(0, arr.shape[0], self.N_C)):
            self.C[f] = arr[st : st + self.N_C]
