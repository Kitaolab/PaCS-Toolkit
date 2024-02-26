import dataclasses
import multiprocessing as mp
import re
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List

import numpy as np
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)
np.set_printoptions(suppress=True)


@dataclasses.dataclass
class SuperAnalyzer(metaclass=ABCMeta):
    CVs: List[float] = None

    @abstractmethod
    def calculate_cv(self, settings: MDsettings, cycle: int) -> List[float]:
        pass

    @abstractmethod
    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        pass

    @abstractmethod
    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        pass

    def write_cv_to_file(
        self, output_file: str, cv_arr: List[Snapshot], settings: MDsettings, cycle: int
    ) -> None:
        dir = settings.each_cycle(_cycle=cycle)
        with open(f"{dir}/summary/{output_file}", "w") as f:
            for snapshot in cv_arr:
                f.write(f"{snapshot}" + "\n")

    def analyze(self, settings: MDsettings, cycle: int) -> List[Snapshot]:
        dir = settings.each_cycle(_cycle=cycle)
        if Path(f"{dir}/summary/cv_ranked.log").exists():
            pattern1 = r"replica (\d+) frame (\d+) cv \[([-\d.\s]+)\]"
            pattern2 = r"replica (\d+) frame (\d+) cv ([-\d.]+)"
            results = []
            with open(f"{dir}/summary/cv_ranked.log", "r") as f:
                for line in f:
                    match1 = re.search(pattern1, line)
                    match2 = re.search(pattern2, line)
                    if match1:
                        replica = int(match1.group(1))
                        frame = int(match1.group(2))
                        cv_values = [float(x) for x in match1.group(3).split()]
                    elif match2:
                        replica = int(match2.group(1))
                        frame = int(match2.group(2))
                        cv_values = float(match2.group(3))
                    else:
                        LOGGER.error(
                            "pattern matching failed. please check the log file."
                        )
                        exit(1)

                    results.append(Snapshot(int(replica), int(frame), cv_values))
            LOGGER.info("analyzer was skipped")
            return results

        pipe_list = []
        n_loop = (settings.n_replica + settings.n_parallel - 1) // settings.n_parallel
        replicas = [x + 1 for x in range(settings.n_replica)]
        for i in range(n_loop):
            job_list = []
            for replica in replicas[
                i
                * settings.n_parallel : min(
                    (i + 1) * settings.n_parallel, settings.n_replica
                )
            ]:
                get_rev, send_rev = mp.Pipe(False)
                p = mp.Process(
                    target=self.calculate_cv, args=(settings, cycle, replica, send_rev)
                )
                job_list.append(p)
                pipe_list.append(get_rev)
                p.start()
            for proc in job_list:
                proc.join()
            for proc in job_list:
                if proc.exitcode != 0:
                    LOGGER.error("error occurred at child process")
                    exit(1)
            # Not necessary, but just in case.
            for proc in job_list:
                proc.close()

        cv_arr = [x.recv() for x in pipe_list]
        assert len(cv_arr) == settings.n_replica

        cv_arr = np.array(cv_arr)
        if len(cv_arr.shape) == 2:
            cv_arr = cv_arr.flatten()
        else:
            cv_arr = cv_arr.reshape(-1, cv_arr.shape[-1])
        n_frame = len(cv_arr) // settings.n_replica

        results: List[Snapshot] = []
        iter = 0
        for rep in range(1, settings.n_replica + 1):
            for frame in range(0, n_frame):
                snapshot = Snapshot(rep, frame, cv_arr[iter])
                iter += 1
                # Exclude the first frame of the trajectory file in gromacs
                # because it is the initial structure
                if settings.simulator == "gromacs" and frame == 0:
                    continue
                results.append(snapshot)

        self.write_cv_to_file("cv.log", results, settings, cycle)
        self.CVs = results[:: settings.skip_frame]
        self.CVs = self.ranking(settings, self.CVs)
        self.write_cv_to_file("cv_ranked.log", self.CVs, settings, cycle)
        LOGGER.info(f"The top ranking CV is {self.CVs[0]}")

        return self.CVs
