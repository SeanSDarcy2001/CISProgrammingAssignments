import numpy as np
from pathlib import Path


class ProblemXBodyY:
    """Parses the LED marker data."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "r") as f:
            line = next(f)
            toks = line.split(" ")
            self.N_m = int(toks[0])     # number of marker LEDs

        arr = np.loadtxt(path, skiprows=1, dtype=np.float64)
        self.Y = arr[: self.N_m]        # marker LEDs in body coordinates
        self.t = arr[self.N_m:]         # tip in body coordinates


class ProblemXMesh:
    """Parses the body surface definition data."""

    def __init__(self, path: str):
        self.path = Path(path)
        with open(path, "r") as f:
            self.N_v = -1
            for i, line in enumerate(f):
                if i == 0:
                    self.N_v = int(line)  # number of vertices
                if i == self.N_v+1:
                    self.N_t = int(line)  # number of triangles

        self.V = np.loadtxt(
            path, skiprows=1, max_rows=self.N_v, dtype=np.float64)
        # vertex indices for triangles
        self.trig = np.loadtxt(path, skiprows=self.N_v+2, dtype=np.float64)


class SampleReadings:
    """Parses the sample readings data."""

    def __init__(self, path):
        self.path = Path(path)
        with open(path, "r") as f:
            line = next(f)
            toks = line.replace(" ", "").split(",")
            # LEDs read by tracker in each sample frame
            self.N_s = int(toks[0])
            self.N_samps = int(toks[1])  # number of sample frames

        arr = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64)
        self.S = np.empty([self.N_samps, self.N_s, 3], np.float64)
        for k, st in enumerate(range(0, arr.shape[0], self.N_s)):
            self.S[k] = arr[st: st + self.N_s]


class OutputReader:
    """Parses a formatted output file for programming assignment 3."""

    def __init__(self, path):
        self.path = Path(path)
        with open(path, "r") as f:
            line = next(f)
            toks = line.split(" ")
            self.N_samps = int(toks[0])

        arr = np.loadtxt(path, delimiter="\t", skiprows=1, dtype=np.float64)
        self.d = np.empty([self.N_samps, 3], np.float64)
        self.c = np.empty([self.N_samps, 3], np.float64)
        self.diff = np.empty([self.N_samps], np.float64)
        for s in range(self.N_samps):
            self.d[s] = arr[s, 0:3]
            self.c[s] = arr[s, 3:6]
            self.diff[s] = arr[s, 6]
