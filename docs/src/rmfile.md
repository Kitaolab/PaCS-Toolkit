# rmfile
- This command is used after executing `pacs mdrun`.
- This command deletes backup files and other unnecessary files.
- This command reduces the number of files and the burden on the computer capacity.

### Caution
- This command is not reversible.

### Example
- The following example removes unnecessary files from the directory.

```shell
pacs rmfile -t 1 -s "gromacs"
```

### Arguments

```plaintext
usage: pacs rmfile [-h] [-t] [-s]
```
- `-t, --trial` (int): 
    - trial number without 0-fill when pacsmd was conducted (e.g. `-t 1`)
- `-s, --simulator` (str): 
    - simulator name (e.g. `-s "gromacs"`)
    - Only `"gromacs"`, `"amber"`, and "`namd`" are accepted.