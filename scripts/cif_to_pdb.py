#!/usr/bin/env python3

from pathlib import Path
from Bio.PDB import MMCIFParser, PDBIO

# ============================================================
# Batch conversion
# ============================================================

def convert_all_cifs(input_dir, output_dir, preserve_structure=False):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    # Collect all CIF files in immediate subdirectories
    cif_files = []
    for subdir in input_path.iterdir():
        if subdir.is_dir():
            cif_files.extend(subdir.glob("*.cif"))

    print(f"Found {len(cif_files)} CIF file(s).\n")

    converted = 0
    skipped = 0
    failed = 0

    for idx, cif_file in enumerate(cif_files, 1):

        # Determine output PDB path
        if preserve_structure:
            relative = cif_file.relative_to(input_path)
            pdb_path = output_path / relative.with_suffix(".pdb")
            pdb_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            pdb_path = output_path / f"{cif_file.stem}.pdb"

        # Skip if already present
        if pdb_path.exists():
            print(f"[{idx}/{len(cif_files)}] {cif_file.name} → {pdb_path.name}  (skipped)")
            skipped += 1
            continue

        print(f"[{idx}/{len(cif_files)}] {cif_file.name} → {pdb_path.name}", end=" ")

        if convert_cif_to_pdb(cif_file, pdb_path):
            print("✓")
            converted += 1
        else:
            print("✗")
            failed += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"Converted: {converted}")
    print(f"Skipped : {skipped}")
    print(f"Failed  : {failed}")
    print(f"Output directory: {output_path.resolve()}")

if __name__ == "__main__":
    INPUT_DIR = "path/to/cif_root"
    OUTPUT_DIR = "path/to/output_pdbs"
    PRESERVE_STRUCTURE = False

    convert_all_cifs(
        input_dir=INPUT_DIR,
        output_dir=OUTPUT_DIR,
        preserve_structure=PRESERVE_STRUCTURE,
    )
