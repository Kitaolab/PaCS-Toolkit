import multiprocessing as mp
from typing import List

from pacs.mdrun.analyzer.superAnalyzer import SuperAnalyzer
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class Template(SuperAnalyzer):
    def calculate_cv(
        self, settings: MDsettings, cycle: int, replica: int, queue: mp.Queue
    ) -> List[float]:
        """
        TODO
        1. Read trajectory based on cycle and replica
        2. Calculate the value that suited the evaluation type.
        3. send the values with the replica number: queue.put((replica, ret))
           (SuperAnalyzer.analyze uses the replica number to keep the order)
        """
        pass

    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        """
        settings: MDsettings
            The settings object contains the parameters for the analysis.
        CVs: List[Snapshot]
            The cv_arr is a list of Snapshot objects
            that contain the CV for each frame in the trajectory.
        TODO:
            Arrange them in ascending, descending, etc.
            order to match the PaCSMD evaluation type.
        Example:
        sorted_cv = sorted(cv_arr, key=lambda x: x.cv)
        return sorted_cv
        """
        pass

    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        if CVs is None:
            CVs = self.CVs
        return CVs[0].cv < settings.threshold
