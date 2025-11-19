#!/usr/bin/env python3
"""
Generate AlphaFold3 JSON input files for TCR:pMHC complexes.

Given:
    - a metadata CSV containing CDR3α and CDR3β sequences
    - a list of PDB IDs

This script:
    1. Downloads FASTA sequences from RCSB.
    2. Identifies each chain (MHC, B2M, peptide, TCRα, TCRβ).
    3. Produces an AF3 JSON input file in the required chain order:
           [MHC, B2M, peptide, TCRα, TCRβ]

Only edit the list `PDB_IDS` and optionally the paths in `CONFIG`.
"""

import os
import json
import requests
import pandas as pd
from io import StringIO
from Bio import SeqIO


# ============================================================
# Configuration (users only modify these)
# ============================================================

CONFIG = {
    "metadata_csv": "ground_truth.csv",        # must contain: PDB ID, CDR3α, CDR3β
    "output_dir": "af_inputs",               # where JSON files will be written
}

# List of PDB IDs to build JSONs for
PDB_IDS = [
    "5e6i", "5isz", "1oga", "2vlr",
    "2vlj", "2vlk", "5tez", "5euo",
]


# ============================================================
# Load CDR3 sequences from CSV
# ============================================================

def load_cdr3_sequences(csv_file):
    """
    Load CDR3α and CDR3β sequences from a metadata CSV.

    Required columns:
        'PDB ID', 'CDR3α', 'CDR3β'

    Returns dict:
        {
            "5e6i": {"cdr3a": "...", "cdr3b": "..."},
            ...
        }
    """
    df = pd.read_csv(csv_file)
    cdr3_map = {}

    for _, row in df.iterrows():
        pdb = str(row["PDB ID"]).lower()
        cdr3_map[pdb] = {
            "cdr3a": str(row["CDR3α"]).strip(),
            "cdr3b": str(row["CDR3β"]).strip(),
        }

    return cdr3_map


# ============================================================
# Download FASTA from RCSB
# ============================================================

def fetch_fasta(pdb_id):
    """Download FASTA records (list of SeqRecord) for a PDB ID."""
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}"
    resp = requests.get(url)

    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch FASTA for {pdb_id} (HTTP {resp.status_code})")

    return list(SeqIO.parse(StringIO(resp.text), "fasta"))


# ============================================================
# Chain Identification
# ============================================================

def classify_chain(seq, pdb_id, cdr3_map):
    """
    Identify chain type using:
      - CDR3α / CDR3β matching
      - generic peptide length (5–20 aa)
      - B2M length heuristic (90–120 aa)
      - MHC heavy chain (>250 aa)
    """
    seq_str = str(seq)
    seq_len = len(seq_str)
    pdb_id = pdb_id.lower()

    # 1. TCR via CDR3 matching
    if pdb_id in cdr3_map:
        if cdr3_map[pdb_id]["cdr3a"] in seq_str:
            return "tcr_alpha"
        if cdr3_map[pdb_id]["cdr3b"] in seq_str:
            return "tcr_beta"

    # 2. Peptide (generic)
    # MHC-I peptides are typically 8–15 aa, rarely 5–20.
    if 5 <= seq_len <= 20:
        return "peptide"

    # 3. B2M (β2-microglobulin)
    if 90 <= seq_len <= 120:
        return "b2m"

    # 4. MHC heavy chain
    if seq_len > 250:
        return "mhc"

    return "unknown"


# ============================================================
# Build AF3 JSON
# ============================================================

def make_af3_json(pdb_id, cdr3_map, outdir):
    """
    Build AF3 JSON in required chain order:
        [MHC, B2M, peptide, TCRα, TCRβ]

    Writes:  <outdir>/<pdb_id>.json
    """
    records = fetch_fasta(pdb_id)

    # storage for final sequence assignment
    chains = {
        "mhc": None,
        "b2m": None,
        "peptide": None,
        "tcr_alpha": None,
        "tcr_beta": None,
    }

    # classify each chain
    for rec in records:
        chain_type = classify_chain(str(rec.seq), pdb_id, cdr3_map)
        if chain_type in chains and chains[chain_type] is None:
            chains[chain_type] = str(rec.seq)

    # detect missing required chains
    missing = [name for name, seq in chains.items() if seq is None]
    if missing:
        print(f"[WARNING] {pdb_id}: missing chains → {missing}")
        return

    # enforce AF3 ordering
    order = ["mhc", "b2m", "peptide", "tcr_alpha", "tcr_beta"]

    sequences = []
    for i, key in enumerate(order):
        sequences.append({
            "protein": {
                "sequence": chains[key],
                "id": chr(ord("A") + i)  # A–E
            }
        })

    job = {
        "name": f"{pdb_id}_tcr_pmhc",
        "modelSeeds": [1],
        "sequences": sequences,
        "dialect": "alphafold3",
        "version": 1,
    }

    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"{pdb_id}.json")

    with open(outfile, "w") as f:
        json.dump(job, f, indent=2)

    print(f"[OK] wrote {outfile}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    cdr3_map = load_cdr3_sequences(CONFIG["metadata_csv"])

    for pdb in PDB_IDS:
        make_af3_json(pdb.lower(), cdr3_map, CONFIG["output_dir"])
