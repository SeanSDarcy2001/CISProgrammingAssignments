import click
import logging
from rich.logging import RichHandler
from rich.progress import track
import time
from pathlib import Path
import numpy as np

from ciscode import readers, Frame, writers, closest, testing, thing, covtree


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger()


@click.command()
@click.option("-d", "--data-dir", default="PA4/data", help="Where the data is.")
@click.option("-o", "--output_dir", default="PA4/outputs", help="Where to store outputs.")
@click.option("-n", "--name", default="PA4-A-Debug", help="Which experiment to run.")
def main(
    data_dir: str = "data", output_dir: str = "outputs", name: str = "BLAHHHH-"
):
    data_dir = Path(data_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir()

    # Read inputs
    A_bod = readers.ProblemXBodyY(data_dir / f"Problem4-BodyA.txt")
    B_bod = readers.ProblemXBodyY(data_dir / f"Problem4-BodyB.txt")
    mesh = readers.ProblemXMesh(data_dir / f"Problem4MeshFile.sur")
    log.debug(mesh)
    sample_readings = readers.SampleReadings(
        data_dir / f"{name}-SampleReadingsTest.txt")

    log.debug("point-cloud to point-cloud registration")

    d = np.empty((sample_readings.N_samps, 3))

    # Start timing
    start_time = time.time()

    for k in track(range(sample_readings.N_samps), "Computing d_k's..."):
        # time.sleep(0.3)
        marks = sample_readings.S[k]
        a = marks[: A_bod.N_m]
        b = marks[A_bod.N_m: A_bod.N_m + B_bod.N_m]

        F_A = Frame.from_points(A_bod.Y, a)
        log.debug(f"{k}: F_A =\n{F_A}")
        F_B = Frame.from_points(B_bod.Y, b)
        log.debug(f"{k}: F_B =\n{F_B}")
        d[k] = F_B.inv().__matmul__(F_A.__matmul__(A_bod.t))

    log.debug("computing s_k points using F_reg")

    c = np.empty((sample_readings.N_samps, 3))
    dists = np.ones((sample_readings.N_samps)) * np.inf

    # Initial guess for PA4
    F_reg = Frame(np.eye(3), np.array([0, 0, 0]))

    # Contruct collection of Triangle Things
    things = []
    for i in range(mesh.N_t):
        points = np.empty((3, 3))
        for q in range(3):
            index = mesh.trig[i, q]
            points[q] = mesh.V[index]
        things.append(thing.TriangleThing(points))

    # Now assume that is an unknown transformation such that
    # c = F*d. F = I, and for
    # Problem 4 you can use this as an initial guess. Compute sample
    # points s = F*d. Now find the points c on the surface mesh that
    # are closest to the s. For
    # Problem 4, you need to use these points to make a new estimate of
    # F and iterate until done.
    tree = covtree.CovTreeNode(things)
    s = F_reg.__matmul__(d)
    tolerance = .00001
    max_iter = 5
    mean_error = 0
    prev_error = 0

    for i in range(max_iter):
        print(i + 1)

        # find the nearest neighbors between the current source and destination points
        for k in track(range(sample_readings.N_samps), "Computing s_k's..."):
            #cov tree
            #if (dists[k] > 2) :
                #s[k] = tree.findClosestPoint(s[k], 1000)
            dists[k], s[k] = closest.find_closest(s[k], mesh.V, mesh.trig)

        #compute the transformation between the current source and nearest destination points
        F_reg = Frame.from_points(d, s)

        # update the current source
        c = F_reg @ d
        for k in track(range(sample_readings.N_samps), "Computing errors's and updating sk...") :
            #cov tree
            #dists[k] = closest.distance(c[k], s[k])
            s[k] = c[k]

        # check error
        mean_error = np.mean(dists)

        #comment out for covtree
        if np.abs(prev_error - mean_error) < tolerance:
            break
        prev_error = mean_error

        print(mean_error)

    # calculate final transformation
    F_reg = Frame.from_points(d, c)

    # End timing
    end_time = time.time()
    log.info(
        f"Execution Time: " f"{end_time - start_time}"
    )

    log.debug("writing output")
    output = writers.PA4(name, d, c, dists)
    output.save(output_dir)

    ref_output_path = data_dir / (name + "-Output.txt")
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

        ans_output_path = data_dir / (name + "-Answer.txt")
        if ans_output_path.exists():
            ans = readers.OutputReader(ans_output_path)

            log.debug(
                "run testing script to validate results against output and answer files given")
            testing.resultsTable(name, output, ref, ans)


if __name__ == "__main__":
    main()
