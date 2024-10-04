import dataclasses
import multiprocessing as mp
import re
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List

import numpy as np
from pacs.models.settings import MDsettings, Snapshot, ScoresInCycle, ScoresInOnePair
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)
np.set_printoptions(suppress=True)


@dataclasses.dataclass
class SuperAnalyzer(metaclass=ABCMeta):
    CVs: List[float] = None

    @abstractmethod
    def calculate_scores_in_one_pair(
        self, settings: MDsettings, cycle: int, fore_replica: int, back_replica: int, send_rev
    ) -> ScoresInOnePair:
        pass

    @abstractmethod
    def aggregate(self, settings: MDsettings, scores_in_cycle: ScoresInCycle, direction: str) -> np.ndarray:
        pass

    @abstractmethod
    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        pass

    @abstractmethod
    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        pass

    def write_cv_to_file(
        self, output_file: str, cv_arr: List[Snapshot], settings: MDsettings, cycle: int, direction: str
    ) -> None:
        dir = settings.each_direction(_cycle=cycle, _direction=direction)
        with open(f"{dir}/summary/{output_file}", "w") as f:
            for snapshot in cv_arr:
                f.write(f"{snapshot}" + "\n")

    def analyze(self, settings: MDsettings, cycle: int) -> List[Snapshot]:
        # call rust functios here
        """
        1. extract the fitting/rmsd part and pass to Rust (fore/back) (remove the center of mass of fitting part by transposing the coordinates)
        2. call rust function to calculate the rmsd matrices for each (fore, back) replica pairs and store them in the disk (shape = (n_frames, n_frames))
        3. read the results from the disk an create a large matrix of rmsd values between all snapshots (shape = (fore_n_replicas, back_n_replicas, n_frames, n_frames))
        4. 全体の行列をもとに、fore/backの各snapshotのrmsdの平均を計算

        1, 2はセットとして、並列化できるようにしておく
        cvをバイナリとしてcycle***/summary/以下に書くのはstep123, テキストとしてcycle***/[fore/back]/summaryに書くのはstep4
        他の評価関数の場合にも使えるよう、一般化しておく（これらはsuperAnalyzer内に書く）
            - あるfore・backのreplicaの組み合わせに対して、そのreplicaの各snapshotの評価関数の値を計算した結果をファイルに書く関数
            - その関数を全ペアに対して回す関数
            - レプリカペアごとになっている.npyファイルを読み込んで、全体の行列を作る関数
        各評価関数ごとにファイル分けして書くべきこと
            - あるfore・backのreplicaの組み合わせに対して、そのreplicaの各snapshotの評価関数の値を計算し、arrで返す関数(rust)
            - 全体の行列をもとに、各replicaの各snapshotの評価関数の平均を計算する関数
        """
        
        replica_pairs = [
            (fore_replica, back_replica) 
            for fore_replica in range(1, settings.n_replica+1) 
            for back_replica in range(1, settings.n_replica+1)
        ]
        
        # calc for the first replica pair
        fore_replica, back_replica = replica_pairs[0]
        scores_in_pair = self.calculate_scores_in_one_pair(settings, cycle, fore_replica, back_replica, None)
        scores_in_cycle = ScoresInCycle(cycle, settings.n_replica, scores_in_pair.n_frames_fore, scores_in_pair.n_frames_back)
        scores_in_cycle.add(scores_in_pair)
        n_frames_fore = scores_in_pair.n_frames_fore
        n_frame_back = scores_in_pair.n_frames_back
        replica_pairs = replica_pairs[1:]

        # calc for the rest replica pairs
        pipe_list = []
        n_loop = (len(replica_pairs) + settings.n_parallel - 1) // settings.n_parallel

        for i in range(n_loop):
            job_list = []
            for fore_replica, back_replica in replica_pairs[
                i * settings.n_parallel : min(
                    (i + 1) * settings.n_parallel, len(replica_pairs)
                )
            ]:
                get_rev, send_rev = mp.Pipe(False)
                p = mp.Process(
                    target=self.calculate_scores_in_one_pair, args=(settings, cycle, fore_replica, back_replica, send_rev)
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

        for pipe in pipe_list:
            scores_in_pair = pipe.recv()
            scores_in_cycle.add(scores_in_pair)
        
        # save the scores_in_cycle to the disk
        path = f"{settings.each_cycle(_cycle=cycle)}/summary/scores_in_cycle.npy"
        scores_in_cycle.save(path)

        # aggregate the scores_in_cycle to the CVs
        cv_arr_fore = self.aggregate(settings, scores_in_cycle, "fore")
        cv_arr_back = self.aggregate(settings, scores_in_cycle, "back")

        results_fore: List[Snapshot] = []
        for rep in range(1, settings.n_replica + 1):
            for frame in range(0, n_frames_fore):
                # Exclude the first frame of the trajectory file in gromacs
                # because it is the initial structure
                if settings.simulator == "gromacs" and frame == 0:
                    continue
                snapshot = Snapshot("fore", rep, frame, cv_arr_fore[rep-1, frame])
                results_fore.append(snapshot)

        results_back: List[Snapshot] = []
        for rep in range(1, settings.n_replica + 1):
            for frame in range(0, n_frame_back):
                # Exclude the first frame of the trajectory file in gromacs
                # because it is the initial structure
                if settings.simulator == "gromacs" and frame == 0:
                    continue
                snapshot = Snapshot("back", rep, frame, cv_arr_back[rep-1, frame])
                results_back.append(snapshot)

        self.write_cv_to_file("cv.log", results_fore, settings, cycle, "fore")
        self.write_cv_to_file("cv.log", results_back, settings, cycle, "back")

        self.fore_CVs = results_fore[:: settings.skip_frame]
        self.back_CVs = results_back[:: settings.skip_frame]

        self.fore_CVs = self.ranking(settings, self.fore_CVs)
        self.back_CVs = self.ranking(settings, self.back_CVs)

        self.write_cv_to_file("cv_ranked.log", self.fore_CVs, settings, cycle, "fore")
        self.write_cv_to_file("cv_ranked.log", self.back_CVs, settings, cycle, "back")

        LOGGER.info(f"The top ranking CV forward is {self.fore_CVs[0]}")
        LOGGER.info(f"The top ranking CV backward is {self.back_CVs[0]}")

        return self.fore_CVs, self.back_CVs


    # def analyze(self, settings: MDsettings, cycle: int) -> List[Snapshot]:
    #     self.analyze(settings, cycle, "fore")
    #     self.analyze(settings, cycle, "back")

    # def analyze_one_way(self, settings: MDsettings, cycle: int, direction: str) -> List[Snapshot]:
    #     dir = settings.each_direction(_cycle=cycle, _direction=direction)
    #     if Path(f"{dir}/summary/cv_ranked.log").exists():
    #         pattern1 = r"replica (\d+) frame (\d+) cv \[([-\d.\s]+)\]"
    #         pattern2 = r"replica (\d+) frame (\d+) cv ([-\d.]+)"
    #         results = []
    #         with open(f"{dir}/summary/cv_ranked.log", "r") as f:
    #             for line in f:
    #                 match1 = re.search(pattern1, line)
    #                 match2 = re.search(pattern2, line)
    #                 if match1:
    #                     replica = int(match1.group(1))
    #                     frame = int(match1.group(2))
    #                     cv_values = [float(x) for x in match1.group(3).split()]
    #                 elif match2:
    #                     replica = int(match2.group(1))
    #                     frame = int(match2.group(2))
    #                     cv_values = float(match2.group(3))
    #                 else:
    #                     LOGGER.error(
    #                         "pattern matching failed. please check the log file."
    #                     )
    #                     exit(1)

    #                 results.append(Snapshot(direction, int(replica), int(frame), cv_values))
    #         LOGGER.info("analyzer was skipped")
    #         return results

    #     pipe_list = []
    #     n_loop = (settings.n_replica + settings.n_parallel - 1) // settings.n_parallel
    #     replicas = [x + 1 for x in range(settings.n_replica)]
    #     for i in range(n_loop):
    #         job_list = []
    #         for replica in replicas[
    #             i
    #             * settings.n_parallel : min(
    #                 (i + 1) * settings.n_parallel, settings.n_replica
    #             )
    #         ]:
    #             get_rev, send_rev = mp.Pipe(False)
    #             p = mp.Process(
    #                 target=self.calculate_cv, args=(settings, cycle, replica, send_rev)
    #             )
    #             job_list.append(p)
    #             pipe_list.append(get_rev)
    #             p.start()
    #         for proc in job_list:
    #             proc.join()
    #         for proc in job_list:
    #             if proc.exitcode != 0:
    #                 LOGGER.error("error occurred at child process")
    #                 exit(1)
    #         # Not necessary, but just in case.
    #         for proc in job_list:
    #             proc.close()

    #     cv_arr = [x.recv() for x in pipe_list]
    #     assert len(cv_arr) == settings.n_replica

    #     cv_arr = np.array(cv_arr)
    #     if len(cv_arr.shape) == 2:
    #         cv_arr = cv_arr.flatten()
    #     else:
    #         cv_arr = cv_arr.reshape(-1, cv_arr.shape[-1])
    #     n_frame = len(cv_arr) // settings.n_replica

    #     results: List[Snapshot] = []
    #     iter = 0
    #     for rep in range(1, settings.n_replica + 1):
    #         for frame in range(0, n_frame):
    #             snapshot = Snapshot(rep, frame, cv_arr[iter])
    #             iter += 1
    #             # Exclude the first frame of the trajectory file in gromacs
    #             # because it is the initial structure
    #             if settings.simulator == "gromacs" and frame == 0:
    #                 continue
    #             results.append(snapshot)

    #     self.write_cv_to_file("cv.log", results, settings, cycle)
    #     self.CVs = results[:: settings.skip_frame]
    #     self.CVs = self.ranking(settings, self.CVs)
    #     self.write_cv_to_file("cv_ranked.log", self.CVs, settings, cycle)
    #     LOGGER.info(f"The top ranking CV is {self.CVs[0]}")

    #     return self.CVs


