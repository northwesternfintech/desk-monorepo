from abc import ABC
from pysrc.exec.action import Action
from pysrc.util.types import Asset

class BaseStrategy(ABC):

    def __init__(self):
        # put any needed state here!
        raise NotImplementedError

    def calculate_actions(self, predictions: dict[Asset, float]) -> list[Action]:
        # calculate actions for your predictions.
        return []
        
