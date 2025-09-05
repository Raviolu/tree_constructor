# Save as scripts/decorateall.py
import subprocess
import argparse
import os

def decorate_trees(root):
    """
    Decorates trees using a custom script, taking treefiles and matrices
    as input and saving diagrams.
    """
    script_path = os.path.join(root, "scripts", "decorate_tree.py")
    treefiles_dir = os.path.join(root, "treefiles")
    matrices_dir = os.path.join(root, "matrices")
    diagrams_dir = os.path.join(root, "diagrams")
    
    assert os.path.exists(script_path), f"No 'decorate_tree.py' script found in '{os.path.join(root, 'scripts')}'!"
    
    if not os.path.exists(treefiles_dir):
        print(f"Error: Treefiles directory not found at '{treefiles_dir}'.")
        return

    os.makedirs(diagrams_dir, exist_ok=True)
    
    name_list = [os.path.splitext(f)[0] for f in os.listdir(treefiles_dir) if f.endswith(".treefile")]

    for name in name_list:
        treefile = os.path.join(treefiles_dir, f"{name}.treefile")
        matrixfile = os.path.join(matrices_dir, f"{name}_data_matrix.tsv")
        outfile_path = os.path.join(diagrams_dir, name) # The decorate script may add its own extension

        if not os.path.exists(matrixfile):
            print(f"Warning: Matrix file for '{name}' not found. Skipping decoration.")
            continue

        print(f"Decorating tree for {name}...")
        # Assuming decorate_tree.py is a Python script that should be executed with python
        command = (
            f"python \"{script_path}\" -t \"{treefile}\" -m \"{matrixfile}\" "
            f"-tm circular -l no -outfile \"{outfile_path}\""
        )
        
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        if process.returncode != 0:
            print(f"Error decorating tree for {name}:\n{process.stderr}")
        else:
            print(f"Finished decorating tree for {name}.")

    print("\nTree decoration process finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Decorate phylogenetic trees with data from matrices.")
    parser.add_argument("-r", "--root", required=True, help="Root directory of the project.")
    args = parser.parse_args()
    decorate_trees(args.root)