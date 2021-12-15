import click
import logging
from rich.logging import RichHandler
from rich.progress import track
import time
from pathlib import Path
import numpy as np

from ciscode import readers, Frame, writers, closest, testing, thing, covariancetree


FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger()


@click.command()
@click.option("-d", "--data-dir", default="PA5/data", help="Where the data is.")
@click.option("-o", "--output_dir", default="PA5/outputs", help="Where to store outputs.")
@click.option("-n", "--name", default="PA5-A-Debug", help="Which experiment to run.")
def main(
    data_dir: str = "data", output_dir: str = "outputs", name: str = "BLAHHHH-"
):
    data_dir = Path(data_dir).resolve()
    output_dir = Path(output_dir).resolve()
    if not output_dir.exists():
        output_dir.mkdir()

    """Read inputs"""
    A_bod = readers.ProblemXBodyY(data_dir / f"Problem5-BodyA.txt")
    B_bod = readers.ProblemXBodyY(data_dir / f"Problem5-BodyB.txt")
    mesh = readers.ProblemXMesh(data_dir / f"Problem5MeshFile.sur")
    modes = readers.Problem5Modes(data_dir / f"Problem5Modes.txt")

    sample_readings = readers.SampleReadings(
        data_dir / f"{name}-SampleReadingsTest.txt")

    log.debug("point-cloud to point-cloud registration")

    d = np.empty((sample_readings.N_samps, 3))

    """Start timing"""
    start_time = time.time()

    for k in track(range(sample_readings.N_samps), "Computing d_k's..."):
        marks = sample_readings.S[k]
        a = marks[: A_bod.N_m]
        b = marks[A_bod.N_m: A_bod.N_m + B_bod.N_m]

        F_A = Frame.from_points(A_bod.Y, a)
        log.debug(f"{k}: F_A =\n{F_A}")
        F_B = Frame.from_points(B_bod.Y, b)
        log.debug(f"{k}: F_B =\n{F_B}")
        d[k] = F_B.inv().__matmul__(F_A.__matmul__(A_bod.t))

    log.debug("computing s_k points using F_reg")

    c = np.zeros((sample_readings.N_samps, 3))
    s = np.empty((sample_readings.N_samps, 3))
    dists = np.ones((sample_readings.N_samps)) * np.inf

    """Initial guess for F_reg"""
    F_reg = Frame(np.eye(3), np.array([0, 0, 0]))

    """Contruct collection of Triangle Things."""
    things = []
    for i in range(mesh.N_t):
        points = np.empty((3, 3))
        for q in range(3):
            index = mesh.trig[i, q]
            points[q] = mesh.V[index]
        things.append(thing.TriangleThing(points))

    """Covtree initialization."""
    #build tree
    tree = covariancetree.CovTreeNode(things, modes.Atlas)
    
    #ICP ICP ICP #ICP

    mean_dist = 0
    convergence = False

    #Lower value means more iterations
    convergence_criteria = .1

    #tune to noise, max d error
    bound = 5

    #iteration index
    i = 0

    newThings = np.copy(things)

    while (convergence == False):

        print("-------------------------------------------")
        print("Iteration", i + 1)
        print("Freg:")
        print(F_reg)

        #update s
        for k in track(range(sample_readings.N_samps), "Updating s points...") :
            s[k] = F_reg.__matmul__(d[k])


        #compute closest point on mesh
        for k in track(range(sample_readings.N_samps), "Computing closest points..."):
            
            #FOR COVTREE
            c[k], triangleOfInterest = tree.findClosestPoint(s[k], c[k], bound)
            #print(triangleOfInterest.corners)
            qs = closest.barycenter(modes.Atlas, tree, triangleOfInterest, c[k])
            # Solve least squares problem
            l = np.linalg.lstsq(qs.T, c[k].T, rcond=1)[0]
            l = l[1:]  # ignore weight for mode 0
            #print(l)

            vert = triangleOfInterest.corners
            p = vert[0]
            t = vert[1]
            u = vert[2]
            pIndex = np.where(tree.points == p)[0][0]
            tIndex = np.where(tree.points == t)[0][0]
            uIndex = np.where(tree.points == u)[0][0]

            v_0 = modes.Atlas[0, pIndex]
            v_m = modes.Atlas[1:, pIndex]
            pUpdate = v_0 + np.dot(l, v_m)

            v_0 = modes.Atlas[0, tIndex]
            v_m = modes.Atlas[1:, tIndex]
            tUpdate = v_0 + np.dot(l, v_m)
           

            v_0 = modes.Atlas[0, uIndex]
            v_m = modes.Atlas[1:, uIndex]
            uUpdate = v_0 + np.dot(l, v_m)

            updatedVertices = np.empty((3, 3))
            updatedVertices[0] = pUpdate
            updatedVertices[0] = tUpdate
            updatedVertices[0] = uUpdate

            newThings[i] = thing.TriangleThing(updatedVertices)

            #print(out)

            #FOR LINEAR
            #dists[k], c[k] = closest.find_closest(s[k], mesh.V, mesh.trig)

        print(len(newThings))
        print(len(things))
        
        #tree = covariancetree.CovTreeNode(newThings, modes.Atlas)

        #3D-3D rigid registration between tracked markers computed closest points
        F_reg = Frame.from_points(d, c)

        #compute changes from previous closest to new closest
        for k in track(range(sample_readings.N_samps), "Computing change...") :
            dists[k] = closest.distance(c[k], s[k])
    

        # check mean shift
        prevMean = np.copy(mean_dist)
        mean_dist = np.mean(dists)
        print("Mean Distance:")
        print(mean_dist)

        #determine convergence
        if (closest.distance(mean_dist, prevMean) < convergence_criteria) :
            convergence = True

        i = i + 1
        print("-------------------------------------------")

    """End timing"""
    end_time = time.time()
    log.info(f"Execution Time: " f"{end_time - start_time}")

    """Write and save output for error calculations."""
    log.debug("writing output")
    output = writers.PA5(name, d, c, dists, mesh)
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
