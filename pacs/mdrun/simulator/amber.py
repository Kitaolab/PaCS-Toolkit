import subprocess
from typing import List

from pacs.mdrun.simulator.superSimulator import SuperSimulator
from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class AMBER(SuperSimulator):
    def run_md(self, settings: MDsettings, cycle: int, replica: int) -> None:
        dir = settings.each_replica(_cycle=cycle, _replica=replica)
        cmd_run = f"{settings.cmd_mpi} {settings.cmd_serial} -O \
                -i {settings.mdconf} \
                -p {settings.topology} \
                -c {dir}/input{settings.structure_extension} \
                -o {dir}/prd.mdout \
                -r {dir}/prd{settings.structure_extension} \
                -inf {dir}/prd.mdinfo \
                -x {dir}/prd{settings.trajectory_extension} \
                1> {dir}/prd.log 2>&1"  # NOQA: E221

        res_run = subprocess.run(cmd_run, shell=True)
        if res_run.returncode != 0:
            LOGGER.error("error occurred at run command")
            LOGGER.error(f"see {dir}/prd.log and {dir}/prd.mdout and {dir}/prd.mdinfo")
            exit(1)

    def run_MPI(
        self, settings: MDsettings, cycle: int, groupreplica: List[int]
    ) -> None:
        groupdir = [
            settings.each_replica(_cycle=cycle, _replica=replica)
            for replica in groupreplica
        ]
        with open(
            f"{settings.each_replica(_cycle=cycle, _replica=groupreplica[0])}/groupfile.txt",
            "w",
        ) as f:
            for dir in groupdir:
                cmd_run = f"-O \
                    -i {settings.mdconf} \
                    -p {settings.topology} \
                    -c {dir}/input{settings.structure_extension} \
                    -o {dir}/prd.mdout \
                    -r {dir}/prd{settings.structure_extension} \
                    -inf {dir}/prd.mdinfo \
                    -x {dir}/prd{settings.trajectory_extension}"  # NOQA: E221
                f.write(cmd_run)
                f.write("\n")
        dir = settings.each_replica(_cycle=cycle, _replica=groupreplica[0])
        cmd_mdrun = f"{settings.cmd_mpi} {settings.cmd_parallel} \
                -ng {len(groupreplica)} -groupfile {dir}/groupfile.txt \
                1> {dir}/prd.log 2>&1"  # NOQA: E221
        res_mdrun = subprocess.run(cmd_mdrun, shell=True)
        if res_mdrun.returncode != 0:
            LOGGER.error("error occurred at run command")
            LOGGER.error(f"see {dir}/prd.log and {dir}/prd.mdout and {dir}/prd.mdinfo")
            exit(1)
