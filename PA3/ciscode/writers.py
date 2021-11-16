from pathlib import Path
import logging

log = logging.getLogger(__name__)


class Writer:
    """Abstract output formatter class."""

    def __init__(self, fname: str):
        self.fname = fname

    def save(self, output_dir: str = "."):
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        with open(output_dir / self.fname, "w") as file:
            file.write(str(self))

        log.info(f"Saved output to {output_dir / self.fname}")


class PA1(Writer):
    """Output formatter class for programming assignment 1."""

    def __init__(self, name: str, em_post, opt_post, C):
        super().__init__(f"{name}-output1.txt")
        self.name = name
        self.em_post = em_post
        self.opt_post = opt_post
        self.C = C
        self.N_frames = C.shape[0]
        self.N_C = C.shape[1]

    def __str__(self):
        outputs = []
        outputs.append(f"{self.N_C}, {self.N_frames}, {self.name}")
        outputs.append(", ".join(map(lambda x: f"  {x:.02f}", self.em_post)))
        outputs.append(", ".join(map(lambda x: f"  {x:.02f}", self.opt_post)))
        outputs += [
            ", ".join(map(lambda x: f"  {x:.02f}", self.C[k, i]))
            for k in range(self.N_frames)
            for i in range(self.N_C)
        ]
        return "\n".join(outputs)
