# How to use

## Installation Requirements: 

```bash
# Install required Python packages
pip install psutil

# For Linux, you might also want:
sudo apt-get install sysstat  # for iostat, mpstat
sudo apt-get install numactl   # for NUMA utilities
```

## Key Features Demonstrated:

1. Cross-platform Memory Information: Works on both Linux and Windows

2. Process Memory Analysis: RSS, VMS, shared memory, page faults

3. Memory Maps: Similar to /proc/pid/maps on Linux

4. Virtual Memory Concepts: Paging, address translation, memory-mapped files

5. System Commands: Wrapper for OS-specific memory commands

6. Memory Allocation Simulation: Demonstrates how memory usage changes

7. Memory Pressure Testing: Shows swapping behavior

## Usage Examples:
1. Run from bash (shell script) 
```bash
python main_memory_simulation.py
```

2. or import the class to your Python script

```python
# Basic usage
mm = MemoryManager()

# Get system memory
print(mm.get_system_memory_info())

# Get process memory
print(mm.get_process_memory_info())

# Monitor memory
mm.monitor_memory_changes(interval=1, duration=10)

# Simulate allocation
mm.simulate_memory_allocation(size_mb=100)
```

