"""
To test cpuinf install the module py-cpuinfo for example
$ conda install conda-forge::py-cpuinfo

or 
$ pip install py-cpuinfo
"""

import cpuinfo
import subprocess
import platform
import re

# Method 1: Using cpuinfo library
info = cpuinfo.get_cpu_info()
print("CPU:", info['brand_raw'])
print("AVX supported:", info.get('avx', False))
print("AVX2 supported:", info.get('avx2', False))
print("AVX512 supported:", info.get('avx512f', False))

# Method 2: Using platform and subprocess
def check_avx_support():
    system = platform.system()
    
    if system == "Linux":
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo_text = f.read()
        has_avx = 'avx' in cpuinfo_text
        has_avx2 = 'avx2' in cpuinfo_text
        has_avx512 = 'avx512' in cpuinfo_text
        
    elif system == "Darwin":  # Mac
        result = subprocess.run(['sysctl', 'machdep.cpu.features'], 
                              capture_output=True, text=True)
        features = result.stdout.lower()
        has_avx = 'avx' in features
        has_avx2 = 'avx2' in features
        has_avx512 = 'avx512' in features
        
    elif system == "Windows":
        # Use wmic command
        result = subprocess.run(['wmic', 'cpu', 'get', 'Name,Instructions'],
                              capture_output=True, text=True)
        features = result.stdout.lower()
        has_avx = 'avx' in features
        has_avx2 = 'avx2' in features
        has_avx512 = 'avx512' in features
    else:
        return {"AVX": False, "AVX2": False, "AVX512": False}
    
    return {"AVX": has_avx, "AVX2": has_avx2, "AVX512": has_avx512}

print("\nAVX Support Check:")
print(check_avx_support()) 


# for GPU 
# install pytorch
# install conda-forge::pytorch
# For NVIDIA GPUs with CUDA
import torch
if torch.cuda.is_available():
    print(f"CUDA GPU: {torch.cuda.get_device_name(0)}")
    print(f"Compute Capability: {torch.cuda.get_device_capability(0)}")
