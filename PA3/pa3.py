import click
import logging
from rich.logging import RichHandler
from rich.progress import track
import time
from pathlib import Path
import numpy as np


from ciscode import readers, Frame, pointer, writers


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("ciscode")


@click.command()
@click.option("-d", "--data-dir", default="PA3/data", help="Where the data is.")
@click.option("-o", "--output_dir", default="PA3/outputs", help="Where to store outputs.")
@click.option("-n", "--name", default="PA3-A-Debug", help="Which experiment to run.")
def main(
    data_dir: str = "data", output_dir: str = "outputs", name: str = "BLAHHHH-"
):
    data_dir = Path(data_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir()

    # Read inputs
    A_bod = readers.ProblemXBodyY(data_dir / f"Problem3-BodyA.txt")
    B_bod = readers.ProblemXBodyY(data_dir / f"Problem3-BodyB.txt")
    mesh = readers.ProblemXMesh(data_dir / f"Problem3MeshFile.sur")
    log.debug(mesh)
    sample_readings = readers.SampleReadings(
        data_dir / f"{name}-SampleReadingsTest.txt")

    log.debug("point-cloud to point-cloud registration")

    d = np.empty((sample_readings.N_samps, 3))

    for k in track(range(sample_readings.N_samps), "Computing d_k's..."):
        time.sleep(0.3)
        marks = sample_readings.S[k]
        a = marks[: A_bod.N_m]
        b = marks[A_bod.N_m: A_bod.N_m + B_bod.N_m]

        F_A = Frame.from_points(A_bod.Y, a)
        log.debug(f"{k}: F_A =\n{F_A}")
        F_B = Frame.from_points(B_bod.Y, b)
        log.debug(f"{k}: F_B =\n{F_B}")
        d[k] = F_B.inv() @ F_A @ A_bod.t

    # log.debug("Problem 2")
    # _, _, em_post = pointer.pivot_calibration(em_pivot.G, return_post=True)

    # log.debug("Problem 3.")
    # beacons_em = np.empty_like(opt_pivot.H)
    # for k in range(opt_pivot.N_frames):
    #     F_D = Frame.from_points(cal_body.d, opt_pivot.D[k])
    #     beacons_em[k] = F_D.inv() @ opt_pivot.H[k]

    # _, _, opt_post = pointer.pivot_calibration(beacons_em, return_post=True)

    # output = writers.PA1(name, em_post, opt_post, C)
    # output.save(output_dir)

    # ref_output_path = data_dir / output.fname
    # if ref_output_path.exists():
    #     ref = readers.OutputReader(ref_output_path)
    #     log.info(
    #         f"EM Post Error: {np.linalg.norm(ref.em_post - output.em_post)}")
    #     log.info(
    #         f"Opt Post Error: {np.linalg.norm(ref.opt_post - output.opt_post)}")
    #     log.info(
    #         f"Mean C_i Error: " f"{np.linalg.norm(ref.C - output.C, axis=-1).mean()}"
    #     )
    #     log.info(
    #         f"Max C_i Error: " f"{np.linalg.norm(ref.C - output.C, axis=-1).max()}"
    #     )


if __name__ == "__main__":
    main()
