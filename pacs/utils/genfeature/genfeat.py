import concurrent.futures
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclass
class GenFeatureCore:
    trial: int
    trj_filename: str
    output_directory: str
    n_parallel: int

    def save(self, cycle: int, replica: int, features: np.ndarray) -> None:
        np.save(
            f"{self.output_directory}/t{self.trial:03}c{cycle:03}r{replica:03}.npy",
            features,
        )
        LOGGER.info(
            f"feature of trial{self.trial:03}cycle{cycle:03}replica{replica:03} was saved at {self.output_directory}/"  # noqa B950
        )

    def prepare(self) -> None:
        output_directory = Path(self.output_directory)
        output_directory.mkdir(parents=True, exist_ok=True)

    def cal_parallel(self, calc_feature, *args, **kwargs) -> None:
        job_dict_list = []

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self.n_parallel
        ) as executor:
            for path in Path(".").glob(f"./trial{self.trial:03}/cycle*/replica*"):
                if not Path(f"{path}/{self.trj_filename}").exists():
                    LOGGER.error(
                        f"trajectory file {path}/{self.trj_filename} is not found."
                    )
                    exit(1)
                cycle = re.findall(r"(\d+)", str(path))[1]
                replica = re.findall(r"(\d+)", str(path))[2]
                trj_path = f"./trial{self.trial:03}/cycle{cycle:03}/replica{replica:03}/{self.trj_filename}"  # noqa B950

                future = executor.submit(calc_feature, trj_path, *args, **kwargs)
                job_dict_list.append(
                    {"future": future, "cycle": cycle, "replica": replica}
                )

            for job_info in job_dict_list:
                future = job_info["future"]
                cycle = job_info["cycle"]
                replica = job_info["replica"]
                result = future.result()
                self.save(cycle, replica, result)
