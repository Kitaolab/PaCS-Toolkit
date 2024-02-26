import subprocess
from typing import List

from pacs.mdrun.simulator.superSimulator import SuperSimulator
from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class NAMD(SuperSimulator):
    def run_md(self, settings: MDsettings, cycle: int, replica: int) -> None:
        dir = settings.each_replica(_cycle=cycle, _replica=replica)
        cmd_cp = f"cat {settings.mdconf} > {dir}/prd.conf"
        res_cp = subprocess.run(cmd_cp, shell=True)
        if res_cp.returncode != 0:
            LOGGER.error("error occurred at cp command")
            exit(1)

        cmd_run = f"{settings.cmd_mpi} {settings.cmd_serial} \
                {dir}/prd.conf 1> {dir}/prd.log 2>&1"
        res_run = subprocess.run(cmd_run, shell=True)
        if res_run.returncode != 0:
            LOGGER.error("error occurred at run command")
            LOGGER.error(f"see {dir}/prd.log")
            exit(1)

    def run_MPI(
        self, settings: MDsettings, cycle: int, groupreplica: List[int]
    ) -> None:
        pass
