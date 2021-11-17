import click
import logging
from rich.logging import RichHandler
from rich.progress import track
import time
from pathlib import Path
import numpy as np


from ciscode import readers, Frame, pointer, writers, closest


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger()


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

    log.debug("computing s_k points using F_reg")

    c = np.empty((sample_readings.N_samps, 3))
    dists = np.empty((sample_readings.N_samps))

    # Assumption for PA3
    F_reg = Frame(np.eye(3, dtype=np.float32), np.array([0, 0, 0]))

    for k in track(range(sample_readings.N_samps), "Computing s_k's..."):
        s = F_reg @ d[k]
        dist, c_k = closest.get_closest_vertex(s, mesh.V)
        c[k] = c_k
        dists[k] = dist

    log.debug("writing output")
    output = writers.PA3(name, d, c, dists)
    output.save(output_dir)

    readout = name + "-Output.txt"
    log.debug(readout)
    log.debug(dists)

    ref_output_path = data_dir / readout
    if ref_output_path.exists():
        ref = readers.OutputReader(ref_output_path)
        log.info(
            f"Mean d Error: " f"{np.linalg.norm(ref.d - output.d, axis=-1).mean()}"
        )
        log.info(
            f"Max d Error: " f"{np.linalg.norm(ref.d - output.d, axis=-1).max()}"
        )

        log.info(
            f"Mean c Error: " f"{np.linalg.norm(ref.c - output.c, axis=-1).mean()}"
        )
        log.info(
            f"Max c Error: " f"{np.linalg.norm(ref.c - output.c, axis=-1).max()}"
        )

        log.info(
            f"Mean Distance Error: " f"{np.linalg.norm(ref.diff - output.diff, axis=-1).mean()}"
        )
        log.info(
            f"Max Distance Error: " f"{np.linalg.norm(ref.diff - output.diff, axis=-1).max()}"
        )


if __name__ == "__main__":
    main()
