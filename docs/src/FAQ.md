# FAQ

***Content***
- [Q: How can I check pacsmd progress ?](#q-how-can-i-check-pacsmd-progress-)
  - [A. You check it by seeing pacsmd standard output or error.](#a-you-check-it-by-seeing-pacsmd-standard-output-or-error)
- [Q: What should I do if there are not evaluation types that I want to use.](#q-what-should-i-do-if-there-are-not-evaluation-types-that-i-want-to-use)
  - [A: Some evaluation types are still in progress. If you need you could also develop by yourself.](#a-some-evaluation-types-are-still-in-progress-if-you-need-you-could-also-develop-by-yourself)
- [Q: dissociation PaCS-MD takes a lot of time. Some simulations could not completed.](#q-dissociation-pacs-md-takes-a-lot-of-time-some-simulations-could-not-completed)
  - [A: Please check COM of selected molecules.](#a-please-check-com-of-selected-molecules)
- [Q: Minor dissociation pathway was obtained. Is is OK ?](#q-minor-dissociation-pathway-was-obtained-is-is-ok-)
  - [A: It really depends on cases but you need to  check carefully by yourself.](#a-it-really-depends-on-cases-but-you-need-to--check-carefully-by-yourself)
- [Q: I got errors during running PaCS-MD](#q-i-got-errors-during-running-pacs-md)
  - [A: Please read the error messages carefully.](#a-please-read-the-error-messages-carefully)


## Q: How can I check pacsmd progress ?
### A. You check it by seeing pacsmd standard output or error.
~~~txt
INFO       2023-12-16 23:22:04  [    parser.py     -       parse      ] input_ims.toml was read successfully
INFO       2023-12-16 23:22:04  [   __main__.py    -      <module>    ] pacsmd version 0.1.1
INFO       2023-12-16 23:22:04  [   __main__.py    -        main      ] PaCS-MD starts
INFO       2023-12-16 23:22:04  [   __main__.py    -     prepare_md   ] MDsettings(..)
INFO       2023-12-16 23:22:04  [   __main__.py    -      pacs_md     ] cycle000 starts
INFO       2023-12-16 23:23:15  [superSimulator.py -  record_finished ] replica001 done
INFO       2023-12-16 23:23:18  [ superAnalyzer.py -      analyze     ] The top ranking CV is replica 1 frame 32 cv 1.864649296784787
INFO       2023-12-16 23:23:19  [     rmmol.py     -    make_top_gmx  ] topology file rmmol_top.pdb has been created in ./trial001/cycle000/replica001
INFO       2023-12-16 23:23:19  [   __main__.py    -      pacs_md     ] cycle000 done
INFO       2023-12-16 23:23:44  [     Cycle.py     -       export     ] export to cycle001 is completed
INFO       2023-12-16 23:23:46  [     rmmol.py     -     rmmol_gmx    ] trajectory file in cycle000 have been reduced
...
~~~

- But sometimes you cannot check it because some supercomputers do not generate log files. If so, you can check it by seeing `trialXXX/cycleXXX/replicaXXX/summary/progress.log`. Here is a sample command for you to check quickly.
~~~shell
 head -n 1 trial001/cycle*/summary/cv_ranked.log | grep frame | awk '{print NR "," $6}'
~~~

And then you can get the following results. First column denotes the cycle number and second column represents CV(for example, COM distance if type == "dissociation").
~~~txt
1,1.864649296784787
2,1.9111852343506632
3,1.9179890510636395
4,1.9223202126596912
5,1.915256901828055
6,1.9316632729334582
7,1.9657408272709807
8,1.9565950015268871
9,1.951968749749852
10,1.9565426138983022
11,1.9765695029520212
12,2.015255318811986
13,2.047009037596073
14,2.0903023704717936
15,2.126198720722031
16,2.1582448887927432
17,2.2197207031516375
18,2.232262081387398
19,2.2752254833312677
20,2.3406157309562796
21,2.372434614483611
22,2.4393667210979166
23,2.480949213506798
24,2.575250861566694
25,2.579432883406738
~~~



## Q: What should I do if there are not evaluation types that I want to use.
### A: Some evaluation types are still in progress. If you need you could also develop by yourself.
- While PaCS-MD offers many evaluation types, we could not incorporate all of them. You're welcome to utilize our template as a reference and develop your own set of evaluation types. [template page](./mdrun/analyzer/template.md).


## Q: dissociation PaCS-MD takes a lot of time. Some simulations could not completed.
### A: Please check COM of selected molecules.
- Sometimes wrong selections might lead to wrong dissociation pathway and free energy.
- But there are some examples where the selections are actually correct but not dissociated based on the initial structure.

- You can check COM quickly by employing the following command.
~~~shell
$ pacs gencom traj mdtraj -s init.gro -t init.gro -ls "resid 168 || resid 253" -o com_of_r168_r253.pdb
$ pacs gencom traj mdtraj -s init.gro -t init.gro -ls "resname Lig" -o com_of_ligand.pdb
$ vmd -m init.gro com_of_r168_r253.pdb com_of_ligand.pdb
~~~


## Q: Minor dissociation pathway was obtained. Is is OK ?
### A: It really depends on cases but you need to  check carefully by yourself.
- Minor pathway may actually emerge, but it could stem from incorrect selections or initial structures, etc. Therefore it's crucial to assess their validity before proceeding with your simulation.


## Q: I got errors during running PaCS-MD
### A: Please read the error messages carefully.
- Since PaCS-MD relies on various other libraries. many issues may arise due to incorrect settings. Before reporting your concerns to Github, please ensure whether the problem genuinely lies with PaCS-MD or not.

- Additionally, since PaCS-MD is often employed on supercomputers, certain issues might be attributed to the supercomputers themselves. For example, PaCS-MD may encounter difficulties running on supercomputers, or errors might arise that are unrelated to the associated libraries.


