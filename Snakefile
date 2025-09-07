import os
import glob

configfile: "config.yaml"

SAMPLES = [
    os.path.basename(f).rsplit('.', 1)[0]
    for ext in ("fna", "fa", "fasta")
    for f in glob.glob(f"raw_data/*.{ext}")
    if ".gitkeep" not in os.path.basename(f)
]


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

rule tree_all:
    input: 
        expand("aligned/{sample}.aln", sample=SAMPLES)
    output:
        expand("treefiles/{sample}.treefile", sample=SAMPLES, allow_missing=True)
    log:
        "logs/tree_all.log"
    shell:
        (
            "python3 scripts/treeall.py -r . -c {config[tree_command]} > {log} 2>&1"
            if config["tree_command"] != ""
            else
            "python3 scripts/treeall.py -r . > {log} 2>&1" 
        )
rule report_missing_treefiles:
    input:
        treefiles=expand("treefiles/{sample}.treefile", sample=SAMPLES, allow_missing=True)
    output:
        "logs/missing_treefiles.txt"
    run:
        missing = [f for f in input.treefiles if not os.path.exists(f)]
        with open(output[0], "w") as out:
            for f in missing:
                out.write(f"{f}\n")
        print(f"Missing treefiles: {missing}")

rule decorate_all:
    input: 
        trees=expand("treefiles/{sample}.treefile", sample=SAMPLES, allow_missing=True),
        matrices=expand("matrices/{sample}_data_matrix.tsv", sample=SAMPLES)
    output:
        expand("diagrams/{sample}.svg", sample=SAMPLES)
    log:
        "logs/decorate_all.log"
    shell:
        "python3 scripts/decorateall.py -r . > {log} 2>&1"
