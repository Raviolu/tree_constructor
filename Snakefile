import os
import glob

configfile: "config.yaml"

SAMPLES = [
    os.path.basename(f).rsplit('.', 1)[0]
    for ext in ("fna", "fa", "fasta")
    for f in glob.glob(f"raw_data/*.{ext}")
    if ".gitkeep" not in os.path.basename(f)
]

# for shell loops

rule all:
    input:
        expand("diagrams/{sample}.svg", sample=SAMPLES, allow_missing=True)

rule align:
    input: 
        "raw_data/{sample}.fna"
    output:
        "aligned/{sample}.aln"
    log:
        "logs/mafft_all_{sample}.log"
    shell:
       "python3 scripts/mafftall.py -f {input} > {log} 2>&1"

rule matrix:
    input: 
        "raw_data/{sample}.fna"
    output:
        "matrices/{sample}_data_matrix.tsv"
    log:
        "logs/matrix_all_{sample}.log"
    shell:
       "python3 scripts/matrixall.py -f {input} -s {config[blast_db]} -e {config[entrez_email]} > {log} 2>&1"

rule tree:
    input:
        "aligned/{sample}.aln"
    output:
        "treefiles/{sample}.treefile"
    log:
        "logs/tree_all_{sample}.log"
    shell:
        (
            "python3 scripts/treeall.py -f {input} -c {config[tree_command]} > {log} 2>&1" 
            if config["tree_command"] != "" 
            else
            "python3 scripts/treeall.py -f {input} > {log} 2>&1"
        )

rule decorate_all:
    input:
        trees=expand("treefiles/{sample}.treefile", sample=SAMPLES, allow_missing=True),
        matrices=expand("matrices/{sample}_data_matrix.tsv", sample=SAMPLES)
    output:
        expand("diagrams/{sample}.svg", sample=SAMPLES, allow_missing=True)
    log:
        "logs/decorate_all.log"
    shell:
        "python3 scripts/decorateall.py -f . > {log} 2>&1"
