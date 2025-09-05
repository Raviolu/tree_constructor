import os
import glob

configfile: "config.yaml"


SAMPLES = [os.path.basename(f).rsplit('.', 1)[0] for f in glob.glob("raw_data/*.fna")] + \
            [os.path.basename(f).rsplit('.', 1)[0] for f in glob.glob("raw_data/*.fa")] + \
            [os.path.basename(f).rsplit('.', 1)[0] for f in glob.glob("raw_data/*.fasta")]


rule all:
    input:
        expand("diagrams/{sample}.svg", sample=SAMPLES)


rule align_all:
    input: 
        glob.glob("raw_data/*.fna"),
        glob.glob("raw_data/*.fasta"),
        glob.glob("raw_data/*.fa")
    output:
        expand("aligned/{sample}.aln", sample=SAMPLES)
    log:
        "logs/mafft_all.log"
    shell:
       "python3 scripts/mafftall.py -r . > {log} 2>&1"

rule matrix_all:
    input: 
        glob.glob("raw_data/*.fna"),
        glob.glob("raw_data/*.fasta"),
        glob.glob("raw_data/*.fa")
    output:
        expand("matrices/{sample}_data_matrix.tsv", sample=SAMPLES)
    log:
        "logs/matrix_all.log"
    shell:
       "python3 scripts/matrixall.py -r . -s {config[blast_db]} -e {config[entrez_email]} > {log} 2>&1"

rule align_all:
    input: 
        expand("aligned/{sample}.aln", sample=SAMPLES)
    output:
        expand("treefiles/{sample}.treefile", sample=SAMPLES)
    log:
        "logs/tree_all.log"
    shell:
       "python3 scripts/treeall.py -r . > {log} 2>&1"

rule decorate_all:
    input: 
        trees=expand("treefiles/{sample}.treefile", sample=SAMPLES),
        matrices=expand("matrices/{sample}_data_matrix.tsv", sample=SAMPLES)
    output:
        expand("diagrams/{sample}.svg", sample=SAMPLES)
    log:
        "logs/decorate_all.log"
    shell:
        "python3 scripts/decorateall.py -r . > {log} 2>&1"
