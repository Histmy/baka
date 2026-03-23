from dataclasses import dataclass
import numpy.typing as npt
import numpy as np


@dataclass
class ToGraph:
    labels: list[list[str]]
    data: npt.NDArray[np.float32]
