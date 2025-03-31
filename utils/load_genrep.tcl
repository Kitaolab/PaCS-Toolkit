
# load files

# mol load pdb rmmol_top.pdb
set trial 17
set trial_str [format "%03d" $trial]

set xtc_name "genrep/t${trial_str}_rep.xtc"
puts $xtc_name
mol load pdb rmmol_top.pdb xtc $xtc_name

mol delrep 0 top

# representation for protein
mol representation NewCartoon
mol selection "protein"
mol color Name
mol material Opaque
mol addrep top

# representation for ligand
mol representation VDW
mol selection "resname LIG"
mol color ColorID ${trial}
mol material Opaque
mol addrep top

# representation for membrane (lipids)
# mol representation QuickSurf
# mol selection "resname CHL PA PC OL"
# mol color ColorID 2
# mol material Transparent
# mol addrep top

# pbc box on ;# display periodic boundary conditions
display projection Orthographic
