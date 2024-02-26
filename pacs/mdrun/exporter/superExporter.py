import dataclasses
import multiprocessing as mp
import re
from abc import ABCMeta, abstractmethod
from typing import List

from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class SuperExporter(metaclass=ABCMeta):
    @abstractmethod
    def export_each(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        results: List[Snapshot],
    ) -> None:
        pass

    def export(self, settings: MDsettings, cycle: int) -> None:
        pattern1 = r"replica (\d+) frame (\d+) cv \[([-\d.\s]+)\]"
        pattern2 = r"replica (\d+) frame (\d+) cv ([-\d.]+)"
        results = []
        dir = settings.each_cycle(_cycle=cycle)
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
                    LOGGER.error("pattern matching failed.")
                    LOGGER.error(f"see {dir}/summary/cv_ranked.log")
                    exit(1)

                results.append(Snapshot(int(replica), int(frame), cv_values))

        if settings.n_replica > len(results):
            LOGGER.error(
                f"The total number of frames now is {len(results)}."
                f"This is less than the number of replicas {settings.n_replica}"
            )
            exit(1)

        n_loop = (settings.n_replica + settings.n_parallel - 1) // settings.n_parallel
        replicas = [i for i in range(settings.n_replica)]
        for i in range(n_loop):
            processes = []
            for rep in replicas[
                i
                * settings.n_parallel : min(
                    (i + 1) * settings.n_parallel, settings.n_replica
                )
            ]:
                p = mp.Process(
                    target=self.export_each, args=(settings, cycle, rep, results)
                )
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
            for p in processes:
                if p.exitcode != 0:
                    LOGGER.error("error occurred at child process")
                    exit(1)
            # Not necessary, but just in case.
            for p in processes:
                p.close()
