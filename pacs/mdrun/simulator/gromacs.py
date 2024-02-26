import multiprocessing as mp
import subprocess
import time as module_time
from pathlib import Path
from typing import List

from pacs.mdrun.simulator.superSimulator import SuperSimulator
from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class GROMACS(SuperSimulator):
    def run_md(self, settings: MDsettings, cycle: int, replica: int) -> None:
        dir = settings.each_replica(_cycle=cycle, _replica=replica)
        self.run_grompp(settings, dir)
        cmd_mdrun = f"{settings.cmd_mpi} {settings.cmd_serial} \
                -deffnm {dir}/prd 1> {dir}/mdrun.log 2>&1"  # NOQA: E221

        # Depending on the supercomputer environment, MPI-related hangs may occur in rare cases.
        # To solve this problem, restart mdrun until log is output
        # This is a useless calculation, but it is better than a hang.
        run_flag = False
        for _ in range(20):
            if Path(f"{dir}/prd.log").exists():
                subprocess.run(f"rm {dir}/prd.log", shell=True)
                module_time.sleep(1)
            process = subprocess.Popen(cmd_mdrun, shell=True)
            module_time.sleep(10)
            if Path(f"{dir}/prd.log").exists():
                run_flag = True
                break
            else:
                process.kill()
                module_time.sleep(5)
        if not run_flag:
            LOGGER.error("mdrun did not start due to some technical errors")
            exit(1)
        process.wait()
        if process.returncode != 0:
            LOGGER.error("error occurred at mdrun command")
            LOGGER.error(f"see {dir}/mdrun.log and {dir}/prd.log")
            exit(1)

    def run_grompp(self, settings: MDsettings, dir: str) -> None:
        cmd_grompp = f"{settings.cmd_gmx} grompp \
                    -f {settings.mdconf} \
                    -o {dir}/prd.tpr \
                    -p {settings.topology} \
                    -c {dir}/input.gro \
                    -n {settings.index_file} \
                    -po {dir}/mdout.mdp \
                    -maxwarn 10 1> {dir}/grompp.log 2>&1"  # NOQA: E221
        res_grompp = subprocess.run(cmd_grompp, shell=True)
        if res_grompp.returncode != 0:
            LOGGER.error("error occurred at grompp command")
            LOGGER.error(f"see {dir}/grompp.log")
            exit(1)

    def run_MPI(
        self, settings: MDsettings, cycle: int, groupreplica: List[int]
    ) -> None:
        groupdir = [
            settings.each_replica(_cycle=cycle, _replica=replica)
            for replica in groupreplica
        ]

        processes = []
        for dir in groupdir:
            p = mp.Process(target=self.run_grompp, args=(settings, dir))
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        for p in processes:
            if p.exitcode != 0:
                LOGGER.error("error occurred at child process")
                exit(1)
        for p in processes:
            p.close()

        groupdirtxt = " ".join(groupdir)
        cmd_mdrun = f"{settings.cmd_mpi} {settings.cmd_parallel} \
                -multidir {groupdirtxt} \
                -deffnm prd \
                1> {dir}/mdrun.log 2>&1"  # NOQA: E221

        # Depending on the supercomputer environment, MPI-related hangs may occur in rare cases.
        # To solve this problem, restart mdrun until log is output
        # This is a useless calculation, but it is better than a hang.
        run_flag = False
        for _ in range(20):
            if Path(f"{groupdir[0]}/prd.log").exists():
                for dir in groupdir:
                    subprocess.run(f"rm {dir}/prd.log", shell=True)
                    module_time.sleep(1)
            process = subprocess.Popen(cmd_mdrun, shell=True)
            module_time.sleep(10)
            if Path(f"{groupdir[0]}/prd.log").exists():
                run_flag = True
                break
            else:
                process.kill()
                module_time.sleep(5)
        if not run_flag:
            LOGGER.error("mdrun did not start due to some technical error")
            exit(1)
        process.wait()
        if process.returncode != 0:
            LOGGER.error("error occurred at mdrun command")
            LOGGER.error(
                f"see mdrun.log and prd.log in each replicas in cycle{cycle:03}"
            )
            exit(1)
