# Basic

There are common settings for any PaCS-MD run. These include the maximum number of cycles to run, how many MD simulations to run in each cycle, and so on. These settings are described in the input file under the `#basic` keyword.

Following are the details of each keyword to be set. For simplicity, we chose "replica" as the MD simulation to be executed in each cycle.

#### keywords

- **max_cycle: int, default=1**
  - Maximum number of cycles to run. (e.g. 100)
  - Minimum value is 1.
  - Maximum value is 999.  
  
- **n_replica: int, default=1**
  - Number of replicas to be excuted in one cycle. (e.g. 50)
  - Minimum value is 1.
  - Maximum value is 999.

- **n_parallel: int, default=1**
  - Number of replicas to be simulated and analyzed in parallel at a time. (e.g. 10)
  - It is recommended that `n_parallel` set to be a divisor of `n_replica`.

- **centering: bool, default=True**
  - This flag controls whether the initial structure of the next cycle is moved to the center of the box at the end of each cycle.
  - if `centering` is true, the initial structure of the next cycle is moved to the center of the box.
  - if `centering` is false, the initial structure of the next cycle will not be moved to the center of the box.
  - For longer MD, the proteins may move away from the center of the box and the features may behave non-intuitively. Therefore, it is recommended to set `centering` to true.

- **centering_selection: str, default="protein" or "Protein" or "@CA,C,O,N,H"**
  - If `centering` is true, the group specified by this keyword moves to the center of the box.
  - If `centering` is false, there is no need to specify this keyword.
  - default value will be changed to match `analyzer`.
    - if `analyzer` == "mdtraj", default="protein"
    - if `analyzer` == "gromacs", default="Protein"
    - if `analyzer` == "cpptraj", default="@CA,C,O,N,H"
- **working_dir: str, default="./."**
  - Directory where pacsmd will run.
- **rmmol: bool, default=false**
  - This flag controls whether the unnecessary molecules will be removed from the trajectory after each cycle.
  - if `rmmol` is true, atoms not specified in the `keep_selection` are removed from the trajectory file.
  - The operation of removing atoms is irreversible.
- **keep_selection: str, (required if `rmmol=true`)**
  - if `rmmol` is true, atoms specified in the `keep_selection` are kept in the trajectory file. (e.g. "protein")
- **rmfile: bool, default=false**
  - This flag controls whether the unnecessary files are removed from the working directory after trial.
  - Backup files and other files are deleted.


#### Example

An example of a basic option in an input file is shown below. This can also be found on [this page](inputfile.md#basic).

```plaintext
max_cycle = 20                     
n_replica = 8                    
n_parallel = 4                    
centering = true                 
centering_selection = "protein"   
working_dir = "/work/"            
rmmol = true                      
keep_selection = "not water"      
rmfile = true                    
```
