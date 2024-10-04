import dataclasses
import re
from pathlib import Path

import numpy as np
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class MDsettings:

    """
    settings for MD simulation

    Attributes:
        trial (int): id of trial
        max_cycle (int): maximum number of cycles
        n_replica (int): number of replicas
        n_parallel (int): number of replicas which are calculated at same time
        centering (bool): whether to center the structure or not in export
        centering_selection (str): selection for centering
        working_dir (Path): working directory
        simulator (str): simulator for MD simulation(gromacs, namd, amber)
        structure (Path): structure file
        topology (Path): topology file
        mdconf (Path): parameter file
        index_file (Path): index file
        trajectory_extension (str): extension of trajectory file
        cmd_mpi (str): command for mpi
        cmd_parallel (str): command for parallel simulation
        cmd_serial (str): command for serial simulation
        analyzer (str): tool for analysis
        type (str): evaluation type
        threshold (float): threshold for evaluation type
        skip_frame (int): number of frames to skip
        reference (Path): reference file
        selection1 (str): selection for evaluation type
        selection2 (str): selection for evaluation type
        selection3 (str): selection for evaluation type
        selection4 (str): selection for evaluation type
        nojump (bool): whether to execute nojump treatment (valid only for gmx)
    """

    # basic
    trial: int = 1
    max_cycle: int = 1
    n_replica: int = 1
    n_parallel: int = 1
    centering: bool = True
    centering_selection: str = None
    working_dir: Path = Path("./.")

    # simulator
    simulator: str = None
    structure_fore: Path = None
    topology_fore: Path = None
    mdconf_fore: Path = None
    index_file_fore: Path = None

    structure_back: Path = None
    topology_back: Path = None
    mdconf_back: Path = None
    index_file_back: Path = None

    trajectory_extension: str = None
    cmd_mpi: str = ""
    cmd_parallel: str = None
    cmd_serial: str = None

    # analyzer
    analyzer: str = "mdtraj"
    type: str = None
    threshold: float = None
    skip_frame: int = 1
    selection1: str = None
    selection2: str = None
    selection3: str = None
    selection4: str = None

    # hidden option
    cmd_gmx: str = None
    top_mdtraj_fore: str = None
    top_mdtraj_back: str = None
    structure_extension: str = None

    # genrepresent option
    # genrepresent: bool = False

    # rmmol option
    rmmol: bool = False
    keep_selection_fore: str = None
    keep_selection_back: str = None

    # rmfile option
    rmfile: bool = False

    # nojump option
    nojump: bool = False

    def each_replica(
        self, _trial: int = None, _cycle: int = None, _direction: str = None, _replica: int = None
    ) -> str:
        if _trial is None:
            _trial = self.trial
        if _cycle is None:
            _cycle = self.max_cycle
        if _replica is None:
            _replica = self.n_replica
        if _direction not in ["fore", "back"]:
            LOGGER.error(f"direction={_direction} is given.")
            exit(1)
        return (
            f"{self.working_dir}/trial{_trial:03}/cycle{_cycle:03}/{_direction}/replica{_replica:03}"
        )

    def each_direction(self, _trial: int = None, _cycle: int = None, _direction: str = None) -> str:
        if _trial is None:
            _trial = self.trial
        if _cycle is None:
            _cycle = self.cycle
        if _direction not in ["fore", "back"]:
            LOGGER.error(f"direction={_direction} is given.")
            exit(1)
        return f"{self.working_dir}/trial{_trial:03}/cycle{_cycle:03}/{_direction}"

    def each_cycle(self, _trial: int = None, _cycle: int = None) -> str:
        if _trial is None:
            _trial = self.trial
        if _cycle is None:
            _cycle = self.cycle
        return f"{self.working_dir}/trial{_trial:03}/cycle{_cycle:03}"

    def each_trial(self, _trial: int = None) -> str:
        if _trial is None:
            _trial = self.trial
        return f"{self.working_dir}/trial{_trial:03}"

    def log_file(self) -> str:
        return f"{self.working_dir}/trial{self.trial:03}.log"

    # def rmmol_top(self, direction: str) -> None:
    #     c0r1_dir = self.each_replica(_cycle=0, _direction=direction, _replica=1)
    #     self.top_mdtraj = f"{c0r1_dir}/rmmol_top.pdb"

    def check_bool(self, value: str) -> bool:
        if isinstance(value, str):
            flag = value.lower()
            return flag in ["true", "1"]
        else:
            return value

    def update(self):
        if self.selection3 is None:
            LOGGER.error("selection3 is None. Please set selection3.")
        if self.selection4 is None:
            LOGGER.error("selection4 is None. Please set selection4.")
        if self.cmd_parallel is None:
            if self.n_parallel > 1:
                LOGGER.warning(
                    ".".join(
                        [
                            "n_parallel is greater than 1",
                            "but cmd_parallel is not set.",
                            "Use cmd_serial instead.",
                        ]
                    )
                )
            self.cmd_parallel = self.cmd_serial

    # def __post_init__(self) -> None:
    def check(self) -> None:
        # int
        self.trial = int(self.trial)
        self.max_cycle = int(self.max_cycle)
        self.n_replica = int(self.n_replica)
        self.n_parallel = int(self.n_parallel)
        self.skip_frame = int(self.skip_frame)
        if self.threshold is not None:
            self.threshold = float(self.threshold)
        if self.trial < 0 or self.trial > 999:
            LOGGER.error(f"trial number {self.trial} is out of range 1..999")
            exit(1)
        if self.max_cycle < 0 or self.max_cycle > 999:
            LOGGER.error(f"cycle number {self.max_cycle} is out of range 1..999")
            exit(1)
        if self.n_replica < 0 or self.n_replica > 999:
            LOGGER.error(f"n_replica number {self.replica} is out of range 1..999")
            exit(1)
        if self.n_parallel < 0 or self.n_parallel > 999:
            LOGGER.error(f"n_parallel number {self.replica} is out of range 1..999")
            exit(1)

        # bool
        self.centering = self.check_bool(self.centering)
        self.rmmol = self.check_bool(self.rmmol)
        # self.genrepresent = self.check_bool(self.genrepresent)
        self.rmfile = self.check_bool(self.rmfile)

        # lower
        if self.type is None:
            LOGGER.error("type is None")
            exit(1)
        if self.simulator is None:
            LOGGER.error("simulator is None")
            exit(1)
        self.simulator = self.simulator.lower()
        self.type = self.type.lower()
        self.analyzer = self.analyzer.lower()

        # simulator
        if self.simulator not in ["gromacs", "namd", "amber"]:
            LOGGER.error(f"{self.simulator} is not supported")
            exit(1)

        # analyzer
        if self.analyzer not in ["mdtraj", "gromacs", "cpptraj"]:
            LOGGER.error(f"{self.analyzer} is not supported")
            exit(1)

        if self.type not in [
            "bd_rmsd",
            # "association",
            # "dissociation",
            # "rmsd",
            # "ee",
            # "a_d",
            # "template",
        ]:
            LOGGER.error(f"{self.type} is not supported")
            exit(1)

        # nojump
        self.nojump = self.check_bool(self.nojump)
        if self.analyzer != "gromacs" or self.simulator != "gromacs":
            LOGGER.warn(
                '"nojump = True" is valid when simulator and analyzer are both "gromacs"'
            )

        # change centering_selection to match analyzer
        if self.analyzer == "mdtraj" and self.centering_selection is None:
            self.centering_selection = "protein"
        if self.analyzer == "cpptraj" and self.centering_selection is None:
            self.centering_selection = "@CA,C,O,N,H"
        if self.analyzer == "gromacs" and self.centering_selection is None:
            self.centering_selection = "Protein"

        # threshold check
        if self.threshold is None and self.type in [
            "bd_rmsd",
            # "target",
            # "association",
            # "dissociation",
            # "rmsd",
        ]:
            LOGGER.error(f"{self.type} requires threshold")
            exit(1)

        if self.simulator != "gromacs" and self.analyzer == "gromacs":
            LOGGER.error("simulator must be gromacs if analyzer is gromacs")
            exit(1)

        # cmd_parallel
        if self.cmd_serial is None:
            LOGGER.error("cmd_serial must be specified")
            exit(1)

        # mpi parallel check
        if self.n_parallel > 1 and self.cmd_mpi == "":
            LOGGER.warning(
                "multiprocessing is used for parallel simulation. \
                        It could be inefficient however. \
                        Therefore, it is recommended to set n_parallel to 1 or cmd_mpi."
            )

        # Check if indexfile is set when gromacs
        if self.simulator == "gromacs" and (self.index_file_fore is None or self.index_file_back is None):
            LOGGER.error("index file is required for gromacs")
            exit(1)

        if self.type in ["target", "rmsd"] and self.reference is None:
            LOGGER.error(f"reference is required for {self.type}")
            exit(1)

        # Whether the required seletion is set in the analyzer
        if self.type == "dissociation":
            if self.selection1 is None:
                LOGGER.error("selection1 is required for dissociation")
                exit(1)
            if self.selection2 is None:
                LOGGER.error("selection2 is required for dissociation")
                exit(1)

        self.update() # update selection3, 4

        if self.topology_fore is None:
            LOGGER.error("topology_fore is None")
            exit(1)
        if self.structure_fore is None:
            LOGGER.error("structure_fore is None")
            exit(1)
        if self.mdconf_fore is None:
            LOGGER.error("mdconf_fore is None")
            exit(1)

        if self.topology_back is None:
            LOGGER.error("topology_back is None")
            exit(1)
        if self.structure_back is None:
            LOGGER.error("structure_back is None")
            exit(1)
        if self.mdconf_back is None:
            LOGGER.error("mdconf_back is None")
            exit(1)

        if self.working_dir is None:
            LOGGER.error("working_dir is None")
            exit(1)
        if self.trajectory_extension is None:
            LOGGER.error("trajectory_extension is None")
            exit(1)

        self.structure_fore = Path(self.structure_fore)
        self.topology_fore = Path(self.topology_fore)
        self.mdconf_fore = Path(self.mdconf_fore)

        self.structure_back = Path(self.structure_back)
        self.topology_back = Path(self.topology_back)
        self.mdconf_back = Path(self.mdconf_back)

        self.working_dir = Path(self.working_dir)
        if self.simulator == "gromacs":
            if self.index_file_fore is None:
                LOGGER.error("index_file_fore is None")
                exit(1)
            if self.index_file_back is None:
                LOGGER.error("index_file_back is None")
                exit(1)
            self.index_file_fore = Path(self.index_file_fore)
            self.index_file_back = Path(self.index_file_back)

        # analyzer
        # if self.type in ["bd_rmsd"]:
        #     self.reference = Path(self.reference)

        # relative path to absolute path
        """
        self.structure = Path(self.structure).resolve()
        self.topology = Path(self.topology).resolve()
        self.mdconf = Path(self.mdconf).resolve()
        self.working_dir = Path(self.working_dir).resolve()
        if self.simulator == "gromacs":
            self.index_file = Path(self.index_file).resolve()

        # analyzer
        if self.type in ["target", "rmsd"]:
            self.reference = Path(self.reference).resolve()
        """

        # gmx command
        if self.simulator == "gromacs" and self.cmd_gmx is None:
            self.cmd_gmx = re.findall(r"\S+", self.cmd_serial)[0]

        # rmmol
        if self.rmmol and (self.keep_selection_fore is None or self.keep_selection_back is None):
            LOGGER.error("keep_selection_[fore/back] are necessary if rmmol is True")
            exit(1)

        # top_mdtraj
        top_extension = [
            ".pdb",
            ".pdb.gz",
            ".h5",
            ".lh5",
            ".prmtop",
            ".parm7",
            ".prm7",
            ".psf",
            ".mol2",
            ".hoomdxml",
            ".gro",
            ".arc",
            ".hdf5",
            ".gsd",
        ]
        # Retrieve the topology file from the input
        # top_mdtraj = next(
        #     (
        #         v
        #         for v in vars(self).values()
        #         if hasattr(v, "as_posix") and v.suffix in top_extension
        #     ),
        #     None,
        # )
        top_mdtraj_fore = Path(self.structure_fore)
        top_mdtraj_back = Path(self.structure_back)
        if top_mdtraj_fore is not None:
            self.top_mdtraj_fore = top_mdtraj_fore
        else:
            LOGGER.error("a topology file required to read the trajectory is missing.")
            exit(1)
        if top_mdtraj_back is not None:
            self.top_mdtraj_back = top_mdtraj_back
        else:
            LOGGER.error("a topology file required to read the trajectory is missing.")
            exit(1)

        # structure_extension
        init_structure_extension = [
            ".xtc",
            ".trr",
            ".pdb",
            ".pdb.gz",
            ".dcd",
            ".h5",
            ".binpos",
            ".nc",
            ".netcdf",
            ".ncrst",
            ".crd",
            ".mdcrd",
            ".ncdf",
            ".lh5",
            ".lammpstrj",
            ".xyz",
            ".xyz.gz",
            ".gro",
            ".rst7",
            ".tng",
            ".dtr",
            ".gsd",
        ]
        tmp_fore = self.structure_fore.suffix
        tmp_back = self.structure_back.suffix
        if tmp_fore != tmp_back:
            # for simplicity, the extension of the structure file must be the same
            LOGGER.error("structure_fore and structure_back must have the same extension.")
            exit(1)
        if tmp_back in init_structure_extension:
            self.structure_extension = tmp_back
        else:
            LOGGER.error(f"cannot start PaCSMD with this STRUCTURE with the extension {tmp_back}")
            exit(1)


class Snapshot:

    """
    information about a snapshot of a trajectory

    Attributes:
        direction (str): direction of simulation [fore, back]
        replica (int): id of replica
        frame (int): id of frame
        cv (float or List[float]): value of collective variable
    """

    def __init__(self, direction: str, replica: int, frame: int, cv: float):
        self.direction = direction
        self.replica = replica
        self.frame = frame
        self.cv = cv

    def __str__(self):
        return f"replica {self.replica} frame {self.frame} cv {self.cv}"

    def __eq__(self, other) -> bool:
        return self.cv == other.cv

    def __lt__(self, other) -> bool:
        return self.cv < other.cv


class ScoresInOnePair:
    """
    Information of CV in a pair of (fore_replica, back_replica)
    """
    def __init__(self, cycle: int, fore_replica: int, back_replica: int, cv_data: np.ndarray) -> None:
        self.cycle: int = cycle
        self.fore_replica: int = fore_replica
        self.back_replica: int = back_replica
        self.cv_data: np.ndarray = cv_data[:]
        self.n_frames_fore: int = self.cv_data.shape[0]
        self.n_frames_back: int = self.cv_data.shape[1]

    
class ScoresInCycle:
    """
    Information of evaluation scores in a cycle

    """
    def __init__(self, cycle: int, n_replicas: int, n_frames_fore: int, n_frames_back: int) -> None:
        self.cycle: int = cycle
        self.n_replicas: int = n_replicas
        self.n_frames_fore: int = n_frames_fore
        self.n_frames_back: int = n_frames_back
        self.cv_data: np.ndarray = np.zeros((n_replicas, n_replicas, n_frames_fore, n_frames_back))

    def add(self, scores_in_one_pair: ScoresInOnePair) -> None:
        # check shape
        fore_replica = scores_in_one_pair.fore_replica
        back_replica = scores_in_one_pair.back_replica
        n_frames_fore = scores_in_one_pair.n_frames_fore
        n_frames_back = scores_in_one_pair.n_frames_back
        if n_frames_fore != self.n_frames_fore:
            raise ValueError(f"n_frames_fore is different: {n_frames_fore} != {self.n_frames_fore}")
        if  n_frames_back != self.n_frames_back:
            raise ValueError(f"n_frames_back is different: {n_frames_back} != {self.n_frames_back}")
        
        # add data
        self.cv_data[scores_in_one_pair.fore_replica-1, scores_in_one_pair.back_replica-1, :, :] = scores_in_one_pair.cv_data
    
    def save(self, path: str) -> None:
        np.save(path, self.cv_data)