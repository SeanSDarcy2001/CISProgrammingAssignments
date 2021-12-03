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


class PA4(Writer):
    """Output formatter class for programming assignment 4."""

    def __init__(self, name: str, d, c, D):
        letter = name.split('-')[1]
        super().__init__(f"pa4-{letter}-Output.txt")
        self.name = name
        self.d = d
        self.c = c
        self.diff = D
        self.N_samps = D.shape[0]

    def __str__(self):
        outputs = []
        outputs.append(f"{self.N_samps}, {self.fname}")
        for i in range(self.N_samps):
            outputs += [
                "  " +
                "   ".join(map(lambda x: f"{x:>6.02f}", self.d[i])) +
                "       " +
                "   ".join(map(lambda x: f"{x:>6.02f}", self.c[i])) +
                f"    {self.diff[i]:>6.03f}"
            ]

        return "\n".join(outputs)
