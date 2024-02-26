# Template

- Template type is a type that can be defined by the user yourself. It is possible to include user-specific variables in input.toml, and these variables can be used in template type in which they are defined.
- This feature embodies the flexibility of PaCS-MD. This is also a feature that recognizes that the development team alone is limited in its ability to support such flexibility.
- This is for advanced users and requires familiarity with PaCS-MD and the simulator used internally (Gromacs, Amber, Namd). If you are not familiar with it, please practice with other types.

*Content*
- [Template](#template)
  - [Step1: Get original source code](#step1-get-original-source-code)
  - [Step2: Code template type](#step2-code-template-type)
    - [calculate\_cv](#calculate_cv)
    - [ranking](#ranking)
    - [is\_threshold](#is_threshold)
  - [Step3: Prepare input.toml](#step3-prepare-inputtoml)
  - [Step4: Run PaCS-MD](#step4-run-pacs-md)


## Step1: Get original source code
- Go to [github repository](https://github.com/Kitaolab/PaCS-Toolkit) and download it.

## Step2: Code template type
- You will see `template.py` is in `pacsmd/md/analyzer/template.py`
- Here is template type
~~~python
class Template(SuperAnalyzer):
    def calculate_cv(self, settings: MDsettings, cycle: int, replica: int, send_rev) -> None:
        """
        TODO
        1. Read trajectory based on self.cycle
        2. Calculate the value that suited the evaluation type.
        3. send the values by send_rev.send(ret_arr)
        """
        pass

    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        """
        CVs: List[Snapshot]
            The CVs is a list of Snapshot objects
            that contain the CV for each frame in the trajectory.
        Snapshot
        TODO:
            Arrange them in ascending, descending, etc.
            order to match the PaCSMD evaluation type.
        Example:
        sorted_cv = sorted(CVs, key=lambda x: x.cv)
        return sorted_cv
        """
        pass

    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        if CVs is None:
            CVs = self.CVs
        return CVs[0].cv < settings.threshold
~~~

- You need to code 3 types mainly (`calculate_cv`, `ranking` and `is_threshold`)

### calculate_cv
- `calcurate_cv` is the core of each evaluation type. Here collective variables(CVs) (distance, RMSD, energy, etc.) are calculated from the MD simulation results in each replica and returned in a list. The evaluation type should be well defined so that the frames are chosen in the direction you wish to sample.
- We recommend you to refer to other evaluation types (e.g. dissociation.py, rmsd.py, etc.).


### ranking
- In `ranking`, the list of CVs calculated by `calcurate_cv` is sorted in descending or ascending order.
- If you want to separate two residues, sort in descending order as the distance increases. Conversely, if you want to bring them closer together, sort in ascending order so that the distance becomes smaller.

### is_threshold
- `is_threshold` determines if the top of the list of CVs (the frame with the most desired CV of all frames) is above or below the threshold set by the user. The inequality should be changed according to the situation.
- If you want to simulate a larger distance, the process would be such that if it goes above a certain distance, it will terminate.


## Step3: Prepare input.toml
- In `input.toml`, you can define variables you want to use.
~~~toml
## analyzer
type = "template"
threshold = "???"

### user defined variable
user-defined-variable1 = 123
user-defined-variable2 = "hoge"
...
~~~

- If you set your variables like the above example, you can use the variables in `template.py` like the following example
~~~python3
class Template(SuperAnalyzer):
    def calculate_cv(self, settings: MDsettings, cycle: int) -> List[float]:
        ...
            if traj.distance > setttings.user-defined-variable1:
                break
        ...

        return list_float
~~~


## Step4: Run PaCS-MD
- Now you can run your original PaCS-MD
~~~shell
pacs mdrun -t 1 -f input.toml
~~~

- Please make a pull_request in [Github](https://github.com/Kitaolab/PaCS-Toolkit) for new possible template scripts.
