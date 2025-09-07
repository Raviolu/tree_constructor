## TREE CONSTRUCTOR

Make trees using IQ-Tree

decorate_tree.py script not included. Inlcude any scripts that you'd like to generate trees that uses -t flag for treefiles and -m flag form matrices

run `conda env create -f tree_builder.yaml && conda activate tree_builder` to create necessary conda env


make a raw_data folder

run `snakemake --cores 4 --use-conda` to run program

initial code written by me, edited by Gemini 2.5 Pro


## TO DO
--> ~~use more robust parseblast outputs to make better matrix~~ DONE 

--> add a setting to add a color col to datamatrix (low priority) 

--> ~~add a config to control tree gen command~~ DONE 

--> Make it easier use decorate_tree scripts (less hardcoding of input commands --> move that to config.yml) 
