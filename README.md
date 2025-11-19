# TCR Structure Prediction and Analysis

## AlphaFold Database Setup
Only need to complete steps in "Obtaining Genetic Databases" section [here](https://github.com/google-deepmind/alphafold3/blob/main/docs/installation.md). AlphaFold can be run using ASU HPC's pre-compiled apptainer image

## Rosetta Applications
Rosetta Relax and Interface Analyzer can be downloaded [here](https://rosettacommons.org/software/download/) as a non-commerical user (version 3.14). 
Required binaries:
`relax.linuxgccrelease`
`InterfaceAnalyzer.linuxgccrelease`

## Input Setup
setup.py only requires a list of PDB IDs and its associated cdr3a and cdr3b sequences. Cdr sequences are only used to enfore canonical chain order where:  
Chain A: MHC  
Chain B: beta-microglobulin  
Chain C: peptide  
Chain D: TCR alpha chain  
Chain E: TCR beta chain  
This ordering is not required; however, it will streamline downstream analysis  

## AlphaFold Prediction
Run predict.sh on input directory. cif_to_pdb.py will convert AlphaFold outputs to a usable format. Run relax.sh on converted pdb files in order to remove steric clashes and correct backbone geometry. 

## Interface Analysis
Run relabel.py on outputs prior to running interface.sh
