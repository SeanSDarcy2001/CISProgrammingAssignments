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


class PA5(Writer):
    """Output formatter class for programming assignment 5."""

    def __init__(self, name: str, s, c, D, m):
        letter = name.split('-')[1]
        super().__init__(f"pa5-{letter}-Output.txt")
        self.name = name
        self.s = s
        self.c = c
        self.diff = D
        self.N_samps = D.shape[0]
        self.N_modes = m.shape[0]

    def __str__(self):
        outputs = []
        outputs.append(f"{self.N_samps}, {self.fname}, {self.N_modes}")

        # Append mode weights
        for i in range(self.N_modes):
            outputs += [
                f"  {self.m[i]:>6.04f}"
            ]

        for i in range(self.N_samps):
            outputs += [
                "  " +
                "   ".join(map(lambda x: f"{x:>6.02f}", self.s[i])) +
                "       " +
                "   ".join(map(lambda x: f"{x:>6.02f}", self.c[i])) +
                f"    {self.diff[i]:>6.03f}"
            ]

        return "\n".join(outputs)
