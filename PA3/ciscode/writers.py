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


class PA3(Writer):
    """Output formatter class for programming assignment 3."""

    def __init__(self, name: str, d, c, mag):
        super().__init__(f"{name}-output1.txt")
        self.name = name
        self.d = d
        self.c = c
        self.diff = mag
        self.N_samps = mag.shape[0]

    def __str__(self):
        outputs = []
        outputs.append(f"{self.N_samps}, {self.name}")
        outputs += [
            (
                "\t".join(map(lambda x: f"  {x:.02f}", self.d[i])),
                "\t".join(map(lambda x: f"  {x:.02f}", self.c[i])),
                "\t".join(map(lambda x: f"  {x:.02f}", self.diff[i])),

            )
            for i in range(self.N_samps)
        ]
        return "\n".join(outputs)
