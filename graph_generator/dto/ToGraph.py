from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class Label:
    name: str
    values: list[str]


@dataclass
class ToGraph:
    labels: list[Label]
    data: npt.NDArray[np.float32]
