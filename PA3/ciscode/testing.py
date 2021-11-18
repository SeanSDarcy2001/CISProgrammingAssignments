from typing import Tuple
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt


# Function to test similarity between given
# output file, computed output values. Outputs
# correctness based on error parameter.
# @Params: comp - some list of computed values for the assignment
#          true - some list of given values for the assignment
#          err  - threshold difference between any two values
# @Returns: acc - % of calculated values that are accurate
def test_similarity(comp, true, err):
    # Checking computed values
    sum_crr = 0
    sum_err = 0
    tot = comp.shape[0]
    for n in range(comp.shape[0]):
        if (np.all(np.fabs(comp[n] - true[n]) < err)):
            sum_crr += 1
        else:
            sum_err += 1
    acc = (100 * sum_crr / tot)
    return acc

# Function to generate % error vs coordinate threshold value plots
# for each debugging set.
# @Params: set - list of debug sets


def resultsTable(name, out, ref, ans):
    thresholds = [.001, 0.0025, 0.005, 0.0075, 0.01, 0.025,
                  0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10]

    outs = [out.d, out.c, out.diff]
    refs = [ref.d, ref.c, ref.diff]
    anss = [ans.d, ans.c, ans.diff]
    comp = [refs, anss]

    output_dir = Path("PA3/plots").resolve()
    if not output_dir.exists():
        output_dir.mkdir()

    for i in range(3):
        for j in range(2):
            inaccuracy = []
            acceptableThres = -1
            found = False

            for thres in thresholds:
                inaccurate = 100 - \
                    test_similarity(outs[i], comp[j][i], thres)
                if (inaccurate < .5 and found == False):
                    acceptableThres = thres
                    found = True
                inaccuracy.append(inaccurate)

            cddiff = ""
            outans = ""
            if i == 0:
                cddiff = "d point coordinates"
            elif i == 1:
                cddiff = "c point coordinates"
            else:
                cddiff = "d - c difference"

            if j == 0:
                outans = "output"
            else:
                outans = "answer"

            plt.figure()
            plt.title("{:s} Threshold for Error Margin: {:.2f}".format(
                name, acceptableThres))
            plt.xlabel("threshold margin of error for {:s}".format(cddiff))
            plt.ylabel(
                "% of points determined to be incorrect compared to {:s} file".format(outans))
            plt.ylim(-.1, 100)
            plt.plot(thresholds, inaccuracy)
            file = "{:s} {:s} thresholds for {:s}".format(name, outans, cddiff)
            plt.savefig(output_dir / file)
