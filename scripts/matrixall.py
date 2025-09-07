from Bio import Entrez, SeqIO
import subprocess
import argparse
import os
import re
import pandas as pd

def blast(filename, db, root):
    """
    Runs BLAST for a given file against a specified database.
    Manages directories and database downloads.
    """
    raw_data_path = os.path.join(root, "raw_data", filename)
    blast_dir = os.path.join(root, "BLAST")
    blast_results_dir = os.path.join(root, "BLAST_results")
    basename = os.path.splitext(filename)[0]
    output_file = os.path.join(blast_results_dir, f"{basename}_b.txt")
    
    db_map = {"mito": "mito", "18S": "SSU_eukaryote_rRNA"}
    db_name = db_map.get(db)
    if not db_name:
        print(f"Error: Invalid database source '{db}'. Choose 'mito' or '18S'.")
        return

    os.makedirs(blast_dir, exist_ok=True)
    os.makedirs(blast_results_dir, exist_ok=True)

    db_path = os.path.join(blast_dir, db_name)
    if not os.path.exists(f"{db_path}.nhr"):
        print(f"Installing the {db_name} BLAST database...")
        cmd = f"cd \"{blast_dir}\" && wget https://ftp.ncbi.nlm.nih.gov/blast/db/{db_name}.tar.gz && tar -xzf {db_name}.tar.gz && rm {db_name}.tar.gz"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        print("Database installed.")

    if os.path.exists(output_file):
        print(f"BLAST results for '{basename}' found. Skipping BLAST.")
        return

    print(f"Running BLAST for {filename}...")
    cmd = f"blastn -query \"{raw_data_path}\" -db \"{db_path}\" -out \"{output_file}\""
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if process.returncode == 0:
        print(f"BLAST completed. Results in '{output_file}'")
    else:
        print(f"BLAST error for {filename}:\n{process.stderr}")

def parse_blast_out_detailed(filepath):

    result = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
    query = None
    for i, line in enumerate(lines):
        if line.startswith('Query='):
            query = line.split('Query=')[1].strip().lstrip('>')
        if query and line.startswith('Sequences producing significant alignments:'):
            for j in range(i+1, len(lines)):
                if lines[j].startswith('>'):
                    desc = lines[j][1:].strip()
                    if (j+1 < len(lines) and lines[j+1].strip() and not lines[j+1].startswith(('Query=', '>'))):
                        desc += ' ' + lines[j+1].strip()
                    length = None
                    for k in range(j, j+10):
                        if k < len(lines) and lines[k].strip().startswith('Length='):
                            length = int(lines[k].strip().split('=')[1])
                            break
                    score, pident = None, None
                    for k in range(j, j+20):
                        if k < len(lines):
                            if m := re.search(r'Score\s*=\s*([\d,]+)', lines[k]):
                                score = int(m.group(1).replace(',', ''))
                            if m2 := re.search(r'Identities\s*=\s*\d+/\d+\s+\((\d+)%\)', lines[k]):
                                pident = int(m2.group(1))
                        if score is not None and pident is not None:
                            break
                    result[query] = [desc, score, length, pident]
                    break
            query = None
    result["name"] = os.path.basename(filepath)
    return result

def create_matrices(blast_results, root, entrez_email):
    """
    Creates data matrices from a list of parsed BLAST result dictionaries.
    """
    Entrez.email = entrez_email 
    matrices_dir = os.path.join(root, "matrices")
    
    for res_dict in blast_results:
        taxa_dict = {}
        info_dict = {}
        basename = res_dict["name"].removesuffix("_b.txt")
        print(f"Fetching taxonomy for {basename}...")
        
        for query_id, hit_info in res_dict.items():
            if query_id == "name":
                continue
            sseqid = hit_info[0].split(" ")[0] # Get accession ID
            try:
                with Entrez.efetch(db='nuccore', id=sseqid, rettype="gb", retmode="text") as handle:
                    record = SeqIO.read(handle, "genbank")
                    taxa_dict[query_id] = record.annotations.get("taxonomy", [])
            except Exception as e:
                print(f"Could not fetch taxonomy for {sseqid} (Query: {query_id}): {e}")
                taxa_dict[query_id] = ["Not Found"]
            info_dict[query_id] = hit_info[1:]


        query_df = pd.DataFrame.from_dict(taxa_dict, orient="index")
        info_df = pd.DataFrame.from_dict(info_dict, orient="index")
        df = query_df.join(info_df, how='inner', lsuffix="_taxa", rsuffix="_info").reset_index()
        outname = os.path.join(matrices_dir, f"{basename}_data_matrix.tsv")
        df.to_csv(outname, sep='\t', index=False)
        print(f"Saved matrix to '{outname}'")

def run_all(root, db, entrez_email):
    raw_data_dir = os.path.join(root, "raw_data")
    matrices_dir = os.path.join(root, "matrices")
    blast_results_dir = os.path.join(root, "BLAST_results")
    os.makedirs(matrices_dir, exist_ok=True)

    name_list = [f for f in os.listdir(raw_data_dir) if os.path.isfile(os.path.join(raw_data_dir, f))]
    
    results_to_process = []
    for filename in name_list:
        basename = os.path.splitext(filename)[0]
        matrix_path = os.path.join(matrices_dir, f"{basename}_data_matrix.tsv")
        if os.path.exists(matrix_path):
            print(f"Matrix for '{basename}' already exists. Skipping.")
            continue
        
        blast(filename, db, root)
        blast_result_file = os.path.join(blast_results_dir, f"{basename}_b.txt")
        if os.path.exists(blast_result_file):
            results_to_process.append(parse_blast_out_detailed(blast_result_file))

    if results_to_process:
        create_matrices(results_to_process, root, entrez_email)
    
    print("\nMatrix generation process finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run BLAST, parse results, and generate taxonomy matrices.")
    parser.add_argument("-r", "--root", required=True, help="Root directory of the project.")
    parser.add_argument("-s", "--source", required=True, choices=['mito', '18S'], help="Input BLAST db (either 'mito' or '18S').")
    parser.add_argument("-e", "--entrez", required=True, help="Entrez email for lookup")
    args = parser.parse_args()
    run_all(args.root, args.source, args.entrez)