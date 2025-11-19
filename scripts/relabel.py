#!/usr/bin/env python3

from pathlib import Path


# ============================================================
# Configuration (edit these)
# ============================================================

INPUT_DIR = "path/to/input_pdbs"
OUTPUT_DIR = "path/to/output_pdbs"

# Expected chain IDs that must all be present before remapping occurs
EXPECTED_CHAINS = {"A", "B", "C", "D", "E"}

# Chain remapping rule:
#   Old → New
CHAIN_MAP = {
    "A": "A",
    "B": "A",
    "C": "A",
    "D": "B",
    "E": "B",
}


# ============================================================
# Relabel chains
# ============================================================

def relabel_pdbs(input_dir, output_dir, chain_map, expected_chains):
    """
    Relabel PDB chains in all files found in input_dir.
    Writes output files into output_dir.

    Args:
        input_dir (Path or str): directory containing .pdb files
        output_dir (Path or str): destination for relabeled .pdb files
        chain_map (dict): mapping from old_chain → new_chain
        expected_chains (set): only remap if ALL of these appear in file
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdb_files = list(input_dir.glob("*.pdb"))
    print(f"Found {len(pdb_files)} PDB file(s).\n")

    for pdb_path in pdb_files:
        # ---- Step 1: detect which chains exist ----
        chains_found = set()

        with open(pdb_path) as f:
            for line in f:
                if line.startswith(("ATOM", "HETATM")):
                    chains_found.add(line[21])  # column 22 (0-indexed 21)

        # ---- Step 2: determine if remapping applies ----
        do_remap = chains_found >= expected_chains

        if do_remap:
            print(f"[REMAP] {pdb_path.name}  (chains = {sorted(chains_found)})")
            output_lines = []

            with open(pdb_path) as f:
                for line in f:
                    if line.startswith(("ATOM", "HETATM")):
                        old = line[21]
                        new = chain_map.get(old, old)
                        line = line[:21] + new + line[22:]
                    output_lines.append(line)

        else:
            print(f"[COPY ] {pdb_path.name}  (chains = {sorted(chains_found)})")
            with open(pdb_path) as f:
                output_lines = f.readlines()

        # ---- Step 3: write output ----
        out_path = output_dir / pdb_path.name
        with open(out_path, "w") as f:
            f.writelines(output_lines)

    print("\nDone — all output written to:", output_dir.resolve())


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    relabel_pdbs(
        input_dir=INPUT_DIR,
        output_dir=OUTPUT_DIR,
        chain_map=CHAIN_MAP,
        expected_chains=EXPECTED_CHAINS,
    )
