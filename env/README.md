# TCRdock Environment Setup (Sol HPC)

## 1. Load mamba
Run this on ASU’s Sol HPC:
```bash
module load mamba/latest
```

## 2. Create the environment
```bash
mamba env create -f /scratch/{USERID}/tcrdock_env.yaml
```

## 3. Activate the environment
```bash
source activate /scratch/{USERID}/tcrdock_env
```

## 4. Apply CUDA library fix
Create a file named `activate.sh` inside your environment directory:
```bash
nano /scratch/{USERID}/tcrdock_env/activate.sh
```

Paste this inside:
```bash
#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/scratch/{USERID}/tcrdock_env/lib
```

Make it executable:
```bash
chmod +x /scratch/ggrama/cse_project/tcrdock_env/activate.sh
```

## 5. Activate the GPU environment in scripts
Add this before running Python in SLURM scripts:
```bash
source /scratch/{USERID}/tcrdock_env/activate.sh
```

## 6. Verify JAX installation (will only work if you initialized your session with GPU support)
```bash
python - << 'EOF'
import jax
print("JAX version:", jax.__version__)
print("Available devices:", jax.devices())
EOF
```
