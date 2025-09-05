import subprocess
import argparse
import os

def align(root):
    """
    Aligns all sequence files from the 'raw_data' directory and saves them
    to the 'aligned' directory.
    """
    raw_data_dir = os.path.join(root, "raw_data")
    aligned_dir = os.path.join(root, "aligned")

    if not os.path.exists(raw_data_dir):
        print(f"Error: Input directory '{raw_data_dir}' not found.")
        return


    os.makedirs(aligned_dir, exist_ok=True)

    name_list = [f for f in os.listdir(raw_data_dir) if os.path.isfile(os.path.join(raw_data_dir, f))]

    for filename in name_list:
        basename = os.path.splitext(filename)[0]
        input_path = os.path.join(raw_data_dir, filename)
        output_path = os.path.join(aligned_dir, f"{basename}.aln")

        if os.path.exists(output_path):
            print(f"Aligned file for '{basename}' already exists. Skipping.")
            continue

        print(f"Aligning {filename}...")
        command = f"mafft --retree 2 \"{input_path}\" > \"{output_path}\""
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        _, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error aligning {filename}:\n{stderr.decode()}")
        else:
            print(f"Successfully aligned {filename} to '{output_path}'")

    print("\nAlignment process finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align all sequences in the raw_data folder using MAFFT.")
    parser.add_argument("-r", "--root", required=True, help="Root directory of the project.")
    args = parser.parse_args()
    align(args.root)