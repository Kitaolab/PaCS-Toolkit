
# load files

set n_trials 30
mol load gro input.gro ;# input.gro of t001/c000/r001

mol delrep 0 top

# representation for protein
mol representation NewCartoon
mol selection "protein"
mol color Name
mol material Opaque
mol addrep top

# representation for ligand
mol representation Licorice
mol selection "resname LIG"
mol color Name
mol material Opaque
mol addrep top

# representation for membrane (lipids)
# mol representation QuickSurf
# mol selection "resname CHL PA PC OL"
# mol color ColorID 2
# mol material Transparent
# mol addrep top

# pbc box on  ;# display periodic boundary conditions
display projection Orthographic

# load files and visualize
for {set trial 1} {$trial <= ${n_trials} } {incr trial} {
    set trial_str [format "%02d" $trial]
    set pdb_name "gencom/pathway_${trial_str}.pdb"
    puts $pdb_name
    mol new $pdb_name waitfor all
    
    # set delete the existing repre and add my repsesentation
    mol delrep 0 top
    mol representation Points
    mol color ColorID ${trial}
    mol addrep top
    mol modstyle 0 top Points 6.0
}