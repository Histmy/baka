from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class ToGraph:
    labels: list[list[str]]
    data: npt.NDArray[np.float32]
