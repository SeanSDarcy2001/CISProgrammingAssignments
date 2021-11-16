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
@click.option("-d", "--data-dir", default="data", help="Where the data is.")
@click.option("-o", "--output_dir", default="outputs", help="Where to store outputs.")
@click.option("-n", "--name", default="pa1-debug-a", help="Which experiment to run.")
def main(
    data_dir: str = "data", output_dir: str = "outputs", name: str = "pa1-debug-a"
):
    data_dir = Path(data_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir()

    # Read inputs
    cal_body = readers.CalBody(data_dir / f"{name}-calbody.txt")
    cal_readings = readers.CalReadings(data_dir / f"{name}-calreadings.txt")
    em_pivot = readers.EMPivot(data_dir / f"{name}-empivot.txt")
    opt_pivot = readers.OptPivot(data_dir / f"{name}-optpivot.txt")

    log.debug("Problem 1")
    C = np.empty((cal_readings.N_frames, cal_body.N_C, 3))

    for k in track(range(cal_readings.N_frames), "Computing C_i's..."):
        time.sleep(0.3)
        F_D = Frame.from_points(cal_body.d, cal_readings.D[k])
        log.debug(f"{k}: F_D =\n{F_D}")
        F_A = Frame.from_points(cal_body.a, cal_readings.A[k])
        log.debug(f"{k}: F_A =\n{F_A}")
        C[k] = F_D.inv() @ F_A @ cal_body.c

    log.debug("Problem 2")
    _, _, em_post = pointer.pivot_calibration(em_pivot.G, return_post=True)

    log.debug("Problem 3.")
    beacons_em = np.empty_like(opt_pivot.H)
    for k in range(opt_pivot.N_frames):
        F_D = Frame.from_points(cal_body.d, opt_pivot.D[k])
        beacons_em[k] = F_D.inv() @ opt_pivot.H[k]

    _, _, opt_post = pointer.pivot_calibration(beacons_em, return_post=True)

    output = writers.PA1(name, em_post, opt_post, C)
    output.save(output_dir)

    ref_output_path = data_dir / output.fname
    if ref_output_path.exists():
        ref = readers.OutputReader(ref_output_path)
        log.info(f"EM Post Error: {np.linalg.norm(ref.em_post - output.em_post)}")
        log.info(f"Opt Post Error: {np.linalg.norm(ref.opt_post - output.opt_post)}")
        log.info(
            f"Mean C_i Error: " f"{np.linalg.norm(ref.C - output.C, axis=-1).mean()}"
        )
        log.info(
            f"Max C_i Error: " f"{np.linalg.norm(ref.C - output.C, axis=-1).max()}"
        )


if __name__ == "__main__":
    main()
