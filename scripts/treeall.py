# Save as scripts/treeall.py
import subprocess
import argparse
import os

def build_trees(root):
    """
    Generates phylogenetic trees for all files in the 'aligned' directory
    and saves them to the 'treefiles' directory.
    """
    aligned_dir = os.path.join(root, "aligned")
    treefiles_dir = os.path.join(root, "treefiles")

    if not os.path.exists(aligned_dir):
        print(f"Error: Aligned directory not found at '{aligned_dir}'. Run alignment first.")
        return

    os.makedirs(treefiles_dir, exist_ok=True)

    name_list = [f for f in os.listdir(aligned_dir) if f.endswith('.aln')]

    for aln_filename in name_list:
        basename = os.path.splitext(aln_filename)[0]
        treefile_path = os.path.join(treefiles_dir, f"{basename}.treefile")
        
        if os.path.exists(treefile_path):
            print(f"Treefile for '{basename}' already exists. Skipping.")
            continue

        print(f"Generating tree for {basename}...")
        aln_file_path = os.path.join(aligned_dir, aln_filename)
        prefix_path = os.path.join(treefiles_dir, basename)
        
        # NOTE: 'nohup' is removed. It is better to run the script in the background
        # from the shell (e.g., `nohup python ... &`) if desired.
        command = f"iqtree -quiet -pre \"{prefix_path}\" -m TEST -alrt 1000 -bb 1000 -nt AUTO -s \"{aln_file_path}\""
        
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            print(f"IQ-TREE error for {basename}:\n{process.stderr}")
        else:
            print(f"Successfully generated tree for {basename}.")

    print("\nTree generation process finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate phylogenetic trees from aligned sequences using IQ-TREE.")
    parser.add_argument("-r", "--root", required=True, help="Root directory of the project.")
    args = parser.parse_args()
    build_trees(args.root)