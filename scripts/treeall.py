import subprocess
import argparse
import os

# In treeall.py

def build_trees(aln_filename, command):
    """
    Generates phylogenetic trees for all files in the 'aligned' directory
    and saves them to the 'treefiles' directory.
    """
    aligned_dir = "aligned"
    treefiles_dir = "treefiles"

    if not os.path.exists(aligned_dir):
        print(f"Error: Aligned directory not found at '{aligned_dir}'. Run alignment first.")
        return

    os.makedirs(treefiles_dir, exist_ok=True)

    # This part is now correct from the last fix
    basename = os.path.splitext(os.path.basename(aln_filename))[0]
    treefile_path = os.path.join(treefiles_dir, f"{basename}.treefile")

    if os.path.exists(treefile_path):
        try:
            # read a small amount to detect placeholder sentinel
            with open(treefile_path, "r") as tf:
                head = tf.read(16)
            if "NO_TREE" in head or os.path.getsize(treefile_path) == 0:
                print(f"Found placeholder for '{basename}', will retry tree generation.")
                try:
                    os.remove(treefile_path)
                    # After removing, we let the code fall through to the 'else' block
                except Exception as e:
                    print(f"Warning: couldn't remove placeholder {treefile_path}: {e}")
                    return # Exit if we can't remove the placeholder
            else:
                print(f"Treefile for '{basename}' already exists. Skipping.")
                return # <<< IMPORTANT: Actually return to skip.
        except Exception:
            print(f"Warning: cannot access existing treefile for '{basename}', skipping regeneration.")
            return # <<< IMPORTANT: Actually return to skip.
    
    # --- The fix is here: this code is now run if the file does NOT exist ---
    print(f"Generating tree for {basename}...")
    aln_file_path = aln_filename
    prefix_path = os.path.join(treefiles_dir, basename)
    
    command = f"iqtree -pre \"{prefix_path}\" {command} -s \"{aln_file_path}\""
    
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(basename + " ran")
    if process.returncode != 0:
        print(f"IQ-TREE error for {basename}:\n{process.stderr}")
        try:
            with open(treefile_path, "w") as tf:
                tf.write("NO_TREE\n")
            print(f"Wrote placeholder treefile for {basename} ({treefile_path}).")
        except Exception as e:
            print(f"Error writing placeholder treefile for {basename}: {e}")
    else:
        print(f"Successfully generated tree for {basename}.")

    print("\nTree generation process finished.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate phylogenetic trees from aligned sequences using IQ-TREE.")
    parser.add_argument("-f", "--file", required=True, help="Root directory of the project.")
    parser.add_argument("-c", "--command", required=False, help="Command to pass to IQ-Tree", default="-m TEST -alrt 1000 -bb 1000 -nt AUTO")
    args = parser.parse_args()

    build_trees(args.file, args.command)