from typing import Tuple
import numpy as np
from .frame import Frame


def pivot_calibration(
    points: np.ndarray, return_post: bool = False
) -> Tuple[Frame, np.ndarray]:
    """Perform a pivot calibration.

    Args:
        points (np.ndarray): [description]

    Returns:
        Tuple[Frame, np.ndarray]: The frame associated with the tool,
            and the location of the tip in that frame. If return_post
            is True, the location of the post in the tracker coordinates
            is also returned.
    """
    F_0 = Frame(np.identity(3), -points[0].mean(axis=0))
    m = 3 * points.shape[0]
    RIs = np.empty((m, 6))
    Ps = np.empty(m)

    for k, st in enumerate(range(0, m, 3)):
        F_0k = Frame.from_points(points[k], points[0])
        F_k = F_0 @ F_0k
        RIs[st : st + 3, :3] = F_k.r
        RIs[st : st + 3, 3:] = -np.identity(3)
        Ps[st : st + 3] = -F_k.p

    x, _, _, _ = np.linalg.lstsq(RIs, Ps, rcond=None)
    post = x[:3]
    tip_tool = x[3:]

    if return_post:
        return F_0, tip_tool, post
    else:
        return F_0, tip_tool
