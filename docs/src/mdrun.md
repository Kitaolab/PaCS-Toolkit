# mdrun
- This command is used to execute PaCS-MD.
- Unlike other commands in pacskit, many variables are set within pacsmd's input file.
- It is assumed that PaCS-MD will first be executed by this command and then analyzed using other commands.
- See [Input file](mdrun/inputfile.md) for details on input files.

### Example
```shell
pacs mdrun -t 1 -f input.toml
```

### Arguments
```plaintext
usage: pacs mdrun [-h] [-t] [-f]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-f, --file` (str): 
    - input file path for PaCS-MD (e.g. `-f input.toml`)