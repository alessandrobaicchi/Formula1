from dataclasses import dataclass
from model.driver import Driver


@dataclass
class Arco:
    d1: Driver
    d2: Driver
    peso: int

