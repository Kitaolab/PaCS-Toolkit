import dataclasses
import multiprocessing as mp
import re
from abc import ABCMeta, abstractmethod
from typing import List

from pacs.models.settings import MDsettings
from pacs.utils.logger import close_logger, generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class SuperSimulator(metaclass=ABCMeta):
    @abstractmethod
    def run_md(self, settings: MDsettings, cycle: int, direction: str, replica: int) -> None:
        pass

    @abstractmethod
    def run_MPI(
        self, settings: MDsettings, cycle: int, direction: str, groupreplica: List[int]
    ) -> None:
        pass

    def run_parallel(self, settings: MDsettings, cycle: int) -> None:
        self.run_parallel_one_way(settings, cycle, "fore")
        self.run_parallel_one_way(settings, cycle, "back")

    def run_parallel_one_way(self, settings: MDsettings, cycle: int, direction: str) -> None:
        if settings.n_parallel == 1 or cycle == 0:
            self.run_serial(settings, cycle, direction)
            return

        if settings.cmd_mpi != "":
            if settings.simulator == "gromacs" or settings.simulator == "amber":
                self.run_parallel_MPI(settings, cycle, direction)
                return

        not_finished_replicas = self.not_finished_replicas(settings, cycle, direction)
        if len(not_finished_replicas) == 0:
            return

        n_parallel = settings.n_parallel
        rest = len(not_finished_replicas)
        n_loop = (rest + n_parallel - 1) // n_parallel
        for i in range(n_loop):
            processes = []
            for replica in not_finished_replicas[
                i * n_parallel : min((i + 1) * n_parallel, rest)
            ]:
                process = mp.Process(
                    target=self.run_md, args=(settings, cycle, replica)
                )
                processes.append(process)
                process.start()

            for process in processes:
                process.join()

            for process in processes:
                if process.exitcode != 0:
                    LOGGER.error("error occurred at child process")
                    exit(1)

            for process in processes:
                process.close()

            for replica in not_finished_replicas[
                i * n_parallel : min((i + 1) * n_parallel, rest)
            ]:
                self.record_finished(settings, cycle, direction, replica)

    def run_serial(self, settings: MDsettings, cycle: int) -> None:
        self.run_serial_one_way(settings, cycle, "fore")
        self.run_serial_one_way(settings, cycle, "back")
    
    def run_serial_one_way(self, settings: MDsettings, cycle: int, direction: str) -> None:
        not_finished_replicas = self.not_finished_replicas(settings, cycle, direction)
        if len(not_finished_replicas) == 0:
            return
        for replica in not_finished_replicas:
            self.run_md(settings, cycle, direction, replica)
            self.record_finished(settings, cycle, direction, replica)

    def not_finished_replicas(self, settings: MDsettings, cycle: int, direction: str) -> List[int]:
        finished_replicas = [False] * settings.n_replica
        dir = settings.each_direction(_cycle=cycle, _direction=direction)
        with open(f"{dir}/summary/progress.log", "r") as f:
            for line in f:
                if "replica" not in line:
                    continue
                replica = int(re.findall(r"\d+", line)[-1])
                finished_replicas[replica - 1] = True

        not_finished_replicas = [
            i + 1 for i, finished in enumerate(finished_replicas) if not finished
        ]
        return not_finished_replicas

    def record_finished(self, settings: MDsettings, cycle: int, direction: str, replica: int) -> None:
        dir = settings.each_direction(_cycle=cycle, _direction=direction)
        logger = generate_logger(f"c{cycle}rep{replica}", f"{dir}/summary/progress.log")
        logger.info(f"replica{replica:03} done")
        close_logger(logger)

    def run_parallel_MPI(self, settings: MDsettings, cycle: int) -> None:
        self.run_parallel_MPI_one_way(settings, cycle, "fore")
        self.run_parallel_MPI_one_way(settings, cycle, "back")
    
    def run_parallel_MPI_one_way(self, settings: MDsettings, cycle: int, direction: str) -> None:
        not_finished_replicas = self.not_finished_replicas(settings, cycle, direction)
        if len(not_finished_replicas) == 0:
            return
        if len(not_finished_replicas) == 1:
            self.run_md(settings, cycle, direction, not_finished_replicas[0])
            self.record_finished(settings, cycle, direction, not_finished_replicas[0])
            return

        n_parallel = settings.n_parallel
        rest = len(not_finished_replicas)
        n_loop = (rest + n_parallel - 1) // n_parallel
        for i in range(n_loop):
            groupreplica = []
            for replica in not_finished_replicas[
                i * n_parallel : min((i + 1) * n_parallel, rest)
            ]:
                groupreplica.append(replica)
            if len(groupreplica) != n_parallel:
                self.run_serial(settings, cycle, direction)
            else:
                self.run_MPI(settings, cycle, direction, groupreplica)
                for replica in groupreplica:
                    self.record_finished(settings, cycle, direction, replica)
