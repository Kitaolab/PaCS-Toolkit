import subprocess
from pathlib import Path

from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def detect_n_replica(settings: MDsettings, cycle: int) -> int:
    # detect number of replicas
    for replica in range(1, 1000):
        replica_dir = Path(settings.each_replica(_cycle=cycle, _replica=replica))
        if not replica_dir.exists():
            n_replica = replica - 1
            break

    if n_replica == 0:
        LOGGER.error(f"replica directory does not exist in cycle{cycle:03}")
        exit(1)
    return n_replica


def detect_n_cycle(settings: MDsettings) -> int:
    max_cycle = 0
    for cycle in range(1000):
        cycle_dir = Path(settings.each_cycle(_cycle=cycle))
        if not cycle_dir.exists():
            max_cycle = cycle - 1
            break
    return max_cycle


def run_rm(file_name: str) -> None:
    cmd_rm = f"rm -f {file_name}"
    res_rm = subprocess.run(cmd_rm, shell=True)
    if res_rm.returncode != 0:
        LOGGER.error(f"error occurred at rm {file_name} command")
        exit(1)


def rmfile(settings: MDsettings, cycle: int) -> None:
    n_replica = detect_n_replica(settings, cycle)
    for replica in range(1, n_replica + 1):
        dir = settings.each_replica(_cycle=cycle, _replica=replica)
        # gromacs
        if settings.simulator == "gromacs":
            # .mdp (mdout.mdp)
            run_rm(f"{dir}/mdout.mdp")

            # .cpt
            run_rm(f"-f {dir}/*.cpt")

            # .tpr
            # keep .tpr files if rmmol=false in mdrun,  in case you want to do rmmol afterward
            if cycle != 0 and settings.rmmol:
                run_rm(f"{dir}/prd.tpr")

            # '#backup#': use -f
            run_rm(f"-f {dir}/\#*")  # NOQA: W605

            # output structure prd
            run_rm(f"{dir}/prd.gro")

        # amber
        elif settings.simulator == "amber":
            # .mdinfo
            run_rm(f"{dir}/prd.mdinfo")

            # # .mdout
            # run_rm(f"{dir}/prd.mdout")

            # prd.log (because empty file)
            run_rm(f"{dir}/prd.log")

            # output structure prd
            run_rm(f"{dir}/prd.rst7")

        # namd
        elif settings.simulator == "namd":
            # .txt
            # run_rm(f"{dir}/*.txt")

            # .conf
            # run_rm(f"{dir}/prd.conf")

            # .coor
            # run_rm(f"{dir}/*.coor")

            # .vel
            # run_rm(f"{dir}/*.vel")

            # .xsc
            # run_rm(f"{dir}/*.xsc")

            # .xst
            # run_rm(f"{dir}/*.xst")

            continue

    LOGGER.info(f"rmfile completed successfully in cycle{cycle:03}")


def rmfile_all(settings: MDsettings) -> None:
    max_cycle = detect_n_cycle(settings)
    for cycle in range(max_cycle + 1):
        rmfile(settings, cycle)
    LOGGER.info("rmfile completed successfully in current trial")
