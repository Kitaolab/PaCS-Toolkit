import subprocess
from pathlib import Path
from typing import Dict

import numpy as np
from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def genrepresent(settings: MDsettings) -> None:
    if settings.analyzer == "mdtraj":
        genrepresent_mdtraj(settings)
    elif settings.analyzer == "gromacs":
        genrepresent_gmx(settings)
    elif settings.analyzer == "cpptraj":
        genrepresent_cpptraj(settings)
    else:
        LOGGER.error("analyze tool is not specified")
        exit(1)


# using mdtraj
def genrepresent_mdtraj(settings: MDsettings) -> None:
    import mdtraj as md

    # create the directory to store the repr trajectory
    repr_dir = make_reprdir(settings)

    # detect the last cycle
    last_cycle = detect_lastcycle(settings)

    # exetract the repr trajectory from each cycle
    ext = settings.trajectory_extension
    trajs = []
    for cycle in range(last_cycle, -1, -1):  # itration until cycle 0
        cycle_dir = settings.each_cycle(_cycle=cycle)
        if cycle == last_cycle:
            selected_replica = 1
        with open(f"{cycle_dir}/summary/cv_ranked.log", "r") as f:
            for idx, line in enumerate(f):
                if idx == (selected_replica - 1):
                    line = line.strip()
                    (_, selected_replica, _, last_frame, _, _) = line.split(" ")
                    last_frame = int(last_frame)
                    selected_replica = int(selected_replica)
                    LOGGER.info(
                        f"cycle: {cycle}, replica: {selected_replica}, frame: {last_frame}"
                    )
                    break

        # extract trajectory
        rep_dir = Path(settings.each_replica(_cycle=cycle, _replica=selected_replica))
        traj = md.load(
            f"{rep_dir}/{settings.trajectory}",
            top=settings.topology,
        )

        extracted_traj = traj[1: last_frame + 1]
        trajs.append(extracted_traj)

    # concatenate the repr trajectory from all cycles
    trajs = trajs[::-1]
    concat_traj = md.join(trajs)
    concat_traj.save(f"{repr_dir}/repr_complete{ext}")

    LOGGER.info("genrepresent has been extracted successfully")


# using gmx
def genrepresent_gmx(settings: MDsettings) -> None:
    # create the directory to store the repr trajectory
    repr_dir = make_reprdir(settings)

    # detect the last cycle
    last_cycle = detect_lastcycle(settings)

    frame_time_dict = load_frame_to_time(settings)

    # exetract the repr trajectory from each cycle
    ext = settings.trajectory_extension
    for cycle in range(last_cycle, -1, -1):  # itration until cycle 0
        cycle_dir = settings.each_cycle(_cycle=cycle)
        if cycle == last_cycle:
            selected_replica = 1
        with open(f"{cycle_dir}/summary/cv_ranked.log", "r") as f:
            for idx, line in enumerate(f):
                if idx == (selected_replica - 1):
                    line = line.strip()
                    (_, selected_replica, _, last_frame, _, _) = line.split(" ")
                    last_frame = int(last_frame)
                    selected_replica = int(selected_replica)
                    LOGGER.info(
                        f"cycle: {cycle}, replica: {selected_replica}, frame: {last_frame}"
                    )
                    break
        rep_dir = Path(settings.each_replica(_cycle=cycle, _replica=selected_replica))
        trj = f"{rep_dir}/{settings.trajectory}"
        top = settings.topology
        # extract trajectory from frame 0 to last_frame, but the first frame is truncated when performing trjcat
        # but only for the first cycle, the first frame is not truncated, so not include the first frame
        first_frame = 1 if cycle == 0 else 0
        cmd_trjconv = f"echo System \
            | {settings.cmd_gmx} trjconv \
            -f {trj} \
            -s {top} \
            -o {repr_dir}/repr_cycle{cycle:03}{ext} \
            -b {frame_time_dict[first_frame]} \
            -e {frame_time_dict[last_frame]} \
            1> {repr_dir}/{cycle}_trjconv.log 2>&1"  # NOQA: E221
        res_trjconv = subprocess.run(cmd_trjconv, shell=True)
        if res_trjconv.returncode != 0:
            LOGGER.error("error occurred at trjconv command")
            exit(1)

    # concatenate the repr trajectory from all cycles
    cmd_trjcat = f"for i in $(seq {last_cycle + 1}); \
        do echo c; done \
        | {settings.cmd_gmx} trjcat \
        -f {repr_dir}/repr_cycle*{ext} \
        -o {repr_dir}/repr_complete{ext} \
        -settime \
        1> {repr_dir}/trjcat.log 2>&1"  # NOQA: E702,E221
    res_trjcat = subprocess.run(cmd_trjcat, shell=True)
    if res_trjcat.returncode != 0:
        LOGGER.error("error occurred at trjcat command")
        exit(1)

    # remove the repr trajectory from each cycle
    res_rm = subprocess.run(f"rm {repr_dir}/repr_cycle*", shell=True)
    if res_rm.returncode != 0:
        LOGGER.error(f"error occurred at rm command in cycle {cycle}")
        exit(1)
    LOGGER.info("genrepresent has been extracted successfully")


def genrepresent_cpptraj(settings: MDsettings) -> None:
    # create the directory to store the repr trajectory
    repr_dir = make_reprdir(settings)

    # detect the last cycle
    last_cycle = detect_lastcycle(settings)

    # exetract the repr trajectory from each cycle
    ext = settings.trajectory_extension
    for cycle in range(last_cycle, -1, -1):  # itration until cycle 0
        cycle_dir = settings.each_cycle(_cycle=cycle)
        if cycle == last_cycle:
            selected_replica = 1
        with open(f"{cycle_dir}/summary/cv_ranked.log", "r") as f:
            for idx, line in enumerate(f):
                if idx == (selected_replica - 1):
                    line = line.strip()
                    (_, selected_replica, _, last_frame, _, _) = line.split(" ")
                    last_frame = int(last_frame)
                    selected_replica = int(selected_replica)
                    LOGGER.info(
                        f"cycle: {cycle}, replica: {selected_replica}, frame: {last_frame}"
                    )
                    break
        rep_dir = Path(settings.each_replica(_cycle=cycle, _replica=selected_replica))
        trj = f"{rep_dir}/{settings.trajectory}"
        top = settings.topology
        cmd_cpptraj = [
            f"parm {top}",
            f"trajin {trj}",
            f"trajout {repr_dir}/repr_cycle{cycle:03}{ext} onlyframes 1-{last_frame + 1}",
            "run",
            "quit",
        ]
        with open(f"{repr_dir}/genrepresent.cpptraj", "w") as f:
            f.write("\n".join(cmd_cpptraj))

        res_cpptraj = subprocess.run(
            f"cpptraj -i {repr_dir}/genrepresent.cpptraj 1> {repr_dir}/genrepresent.log \
                    2> {repr_dir}/genrepresent.log --log {repr_dir}/repr_dir.log",
            shell=True,
        )
        if res_cpptraj.returncode != 0:
            LOGGER.error("error occurred at cpptraj command")
            exit(1)

    # concatenate the repr trajectory from all cycles
    cmd_cpptraj = [
        f"parm {top}",
        f"trajin {repr_dir}/repr_cycle*{ext}",
        f"trajout {repr_dir}/repr_complete{ext}",
        "run",
        "quit",
    ]
    with open(f"{repr_dir}/trjcat.cpptraj", "w") as f:
        f.write("\n".join(cmd_cpptraj))
    res_cpptraj = subprocess.run(
        f"cpptraj -i {repr_dir}/trjcat.cpptraj 1> {repr_dir}/trjcat.log \
                2>&1 {repr_dir}/trjcat.log --log {repr_dir}/trjcat.log",
        shell=True,
    )

    # Combining trajectories using cpptraj in pacsmd will cause error
    # So even returncode is 1, pacsmd will ignore
    # if res_cpptraj.returncode != 0:
    #     LOGGER.error("error occurred at cpptraj command")
    #     exit(1)

    # remove the repr trajectory from each cycle
    res_rm = subprocess.run(f"rm {repr_dir}/repr_cycle*", shell=True)
    if res_rm.returncode != 0:
        LOGGER.error(f"error occurred at rm command in cycle {cycle}")
        exit(1)
    LOGGER.info("genrepresent has been extracted successfully")


def load_frame_to_time(settings: MDsettings) -> Dict[int, float]:
    # Read correspondence between frame and time from file
    dir_0_1 = settings.each_replica(_cycle=0, _replica=1)
    # load frame to time (no need to do "skiprows=1" because it is recognized as a commment line by default)
    frame_time_array = np.loadtxt(
        f"{dir_0_1}/frame_time.tsv", comments="#", delimiter="\t", skiprows=0
    )
    frame_time_dict: Dict[int, float] = {}
    for frame, time in frame_time_array:
        frame_time_dict[int(frame)] = time
    return frame_time_dict


def detect_lastcycle(settings: MDsettings) -> int:
    # detect the last cycle
    last_cycle = 0
    for cycle in range(1, settings.max_cycle + 1):
        cycle_dir = Path(settings.each_cycle(_cycle=cycle))
        if not (cycle_dir / "summary/cv_ranked.log").exists():
            last_cycle = cycle - 1
            break
    if last_cycle == 0:
        LOGGER.error("cv_ranked.log is not found")
        LOGGER.error("please check the simulation")
        exit(1)
    return last_cycle


def make_reprdir(settings: MDsettings) -> Path:
    # create the directory to store the repr trajectory
    repr_dir = Path(f"{settings.each_trial()}/genrepresent")
    if not repr_dir.exists():
        repr_dir.mkdir(parents=True)
    return repr_dir
