"""
Memory and Virtual Memory Management Demonstrator
Works on both Linux and Windows
"""

import os
import sys
import platform
import subprocess
import psutil
import time
import ctypes
import mmap
import struct
from typing import Dict, List, Optional, Tuple
import threading

class MemoryManager:
    """Cross-platform memory management demonstrations"""
    
    def __init__(self):
        self.system = platform.system()
        print(f"Running on: {self.system}")
        print(f"Python version: {sys.version}\n")
        
    def get_system_memory_info(self) -> Dict:
        """Get system-wide memory information"""
        mem_info = {}
        
        if self.system == "Linux":
            try:
                # Read /proc/meminfo
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            mem_info[key.strip()] = value.strip()
                
                # Get swap info
                swap_info = psutil.swap_memory()
                mem_info['Swap Total'] = f"{swap_info.total / (1024**3):.2f} GB"
                mem_info['Swap Used'] = f"{swap_info.used / (1024**3):.2f} GB"
                mem_info['Swap Free'] = f"{swap_info.free / (1024**3):.2f} GB"
                
            except Exception as e:
                print(f"Error reading /proc/meminfo: {e}")
                
        elif self.system == "Windows":
            try:
                # Use psutil for Windows
                virtual_mem = psutil.virtual_memory()
                swap_mem = psutil.swap_memory()
                
                mem_info = {
                    'Total Memory': f"{virtual_mem.total / (1024**3):.2f} GB",
                    'Available Memory': f"{virtual_mem.available / (1024**3):.2f} GB",
                    'Used Memory': f"{virtual_mem.used / (1024**3):.2f} GB",
                    'Memory Percent': f"{virtual_mem.percent}%",
                    'Swap Total': f"{swap_mem.total / (1024**3):.2f} GB",
                    'Swap Used': f"{swap_mem.used / (1024**3):.2f} GB",
                    'Swap Free': f"{swap_mem.free / (1024**3):.2f} GB",
                }
            except Exception as e:
                print(f"Error getting Windows memory info: {e}")
        
        return mem_info
    
    def get_process_memory_info(self, pid: Optional[int] = None) -> Dict:
        """Get memory information for a specific process"""
        if pid is None:
            pid = os.getpid()
        
        try:
            process = psutil.Process(pid)
            mem_info = process.memory_info()
            mem_percent = process.memory_percent()
            
            return {
                'PID': pid,
                'RSS (Resident Set Size)': f"{mem_info.rss / 1024 / 1024:.2f} MB",
                'VMS (Virtual Memory Size)': f"{mem_info.vms / 1024 / 1024:.2f} MB",
                'Shared Memory': f"{mem_info.shared / 1024 / 1024:.2f} MB" if hasattr(mem_info, 'shared') else 'N/A',
                'Text': f"{mem_info.text / 1024 / 1024:.2f} MB" if hasattr(mem_info, 'text') else 'N/A',
                'Data': f"{mem_info.data / 1024 / 1024:.2f} MB" if hasattr(mem_info, 'data') else 'N/A',
                'Memory Percent': f"{mem_percent:.2f}%",
                'Page Faults': mem_info.num_page_faults if hasattr(mem_info, 'num_page_faults') else 'N/A',
            }
        except Exception as e:
            return {'Error': f"Failed to get process memory info: {e}"}
    
    def get_memory_maps(self, pid: Optional[int] = None) -> List[Dict]:
        """Get memory maps for a process (similar to /proc/pid/maps on Linux)"""
        if pid is None:
            pid = os.getpid()
        
        maps = []
        try:
            process = psutil.Process(pid)
            
            if self.system == "Linux":
                # Read /proc/pid/maps directly for more details
                try:
                    with open(f'/proc/{pid}/maps', 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                addr_range, perms, offset, dev, inode = parts[:5]
                                pathname = parts[-1] if len(parts) > 5 else ''
                                
                                start_end = addr_range.split('-')
                                if len(start_end) == 2:
                                    start_addr = int(start_end[0], 16)
                                    end_addr = int(start_end[1], 16)
                                    size = end_addr - start_addr
                                    
                                    maps.append({
                                        'start': f"0x{start_addr:016x}",
                                        'end': f"0x{end_addr:016x}",
                                        'size': f"{size / 1024:.2f} KB",
                                        'perms': perms,
                                        'offset': offset,
                                        'path': pathname
                                    })
                except Exception as e:
                    print(f"Error reading /proc/{pid}/maps: {e}")
                    
            elif self.system == "Windows":
                # Use psutil's memory_maps (requires admin privileges on Windows)
                try:
                    for mem_map in process.memory_maps():
                        maps.append({
                            'path': mem_map.path,
                            'rss': f"{mem_map.rss / 1024:.2f} KB",
                            'size': f"{mem_map.size / 1024:.2f} KB",
                            'perms': mem_map.perms,
                        })
                except Exception as e:
                    print(f"Note: Detailed memory maps require admin privileges on Windows: {e}")
        
        except Exception as e:
            print(f"Error getting memory maps: {e}")
        
        return maps
    
    def simulate_memory_allocation(self, size_mb: int = 100):
        """Simulate memory allocation and monitor its effects"""
        print(f"\n=== Simulating Memory Allocation ({size_mb} MB) ===")
        
        # Get initial memory usage
        initial_mem = self.get_process_memory_info()
        print(f"Initial memory usage: {initial_mem.get('RSS (Resident Set Size)', 'N/A')}")
        
        # Allocate memory
        try:
            # Allocate a list of bytes
            chunk_size = 1024 * 1024  # 1 MB
            allocated_memory = []
            
            for i in range(size_mb):
                # Allocate 1 MB chunk
                chunk = bytearray(chunk_size)
                allocated_memory.append(chunk)
                
                # Periodically show progress
                if (i + 1) % 10 == 0 or i == size_mb - 1:
                    current_mem = self.get_process_memory_info()
                    print(f"Allocated {i + 1} MB, Current RSS: {current_mem.get('RSS (Resident Set Size)', 'N/A')}")
                    time.sleep(0.1)  # Small delay to see progression
            
            print(f"\nAllocated {size_mb} MB successfully")
            
            # Show final memory usage
            final_mem = self.get_process_memory_info()
            print(f"Final memory usage: {final_mem.get('RSS (Resident Set Size)', 'N/A')}")
            
            # Keep memory allocated for a while
            print("Holding allocated memory for 5 seconds...")
            time.sleep(5)
            
        except MemoryError:
            print(f"MemoryError: Could not allocate {size_mb} MB!")
        finally:
            # Explicitly free memory
            allocated_memory.clear()
            import gc
            gc.collect()
            
            print("Memory freed. Final state:")
            print(self.get_process_memory_info())
    
    def monitor_memory_changes(self, interval: float = 1.0, duration: float = 10.0):
        """Monitor memory usage changes over time"""
        print(f"\n=== Monitoring Memory Changes (for {duration} seconds) ===")
        
        end_time = time.time() + duration
        samples = []
        
        while time.time() < end_time:
            mem_info = self.get_process_memory_info()
            samples.append({
                'time': time.time(),
                'rss': mem_info.get('RSS (Resident Set Size)', '0 MB')
            })
            time.sleep(interval)
        
        print(f"\nCollected {len(samples)} samples:")
        for i, sample in enumerate(samples):
            print(f"Sample {i + 1}: {sample['rss']}")
    
    def run_linux_memory_commands(self):
        """Run Linux-specific memory commands"""
        if self.system != "Linux":
            print("Linux-specific commands only work on Linux")
            return
        
        commands = {
            'System Architecture': 'uname -a',
            'Page Size': 'getconf PAGE_SIZE',
            'Memory Info': 'cat /proc/meminfo | head -20',
            'Buddy Info (memory fragmentation)': 'cat /proc/buddyinfo',
            'VM Stats': 'vmstat 1 3',
            'Top Memory Processes': 'ps aux --sort=-%mem | head -10',
            'Page Fault Stats': 'ps -eo min_flt,maj_flt,cmd | head -10',
        }
        
        print("\n=== Linux Memory Commands ===")
        for desc, cmd in commands.items():
            print(f"\n{desc}:")
            print("-" * 40)
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
            except Exception as e:
                print(f"Error: {e}")
    
    def run_windows_memory_commands(self):
        """Run Windows-specific memory commands"""
        if self.system != "Windows":
            print("Windows-specific commands only work on Windows")
            return
        
        commands = {
            'System Info': 'systeminfo | findstr /C:"Total Physical Memory" /C:"Available Physical Memory"',
            'Memory Usage': 'wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Format:Value',
            'Process List': 'tasklist /FI "MEMUSAGE gt 100000"',
            'Page File Info': 'wmic pagefile list /format:list',
        }
        
        print("\n=== Windows Memory Commands ===")
        for desc, cmd in commands.items():
            print(f"\n{desc}:")
            print("-" * 40)
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
            except Exception as e:
                print(f"Error: {e}")
    
    def demonstrate_virtual_memory_concepts(self):
        """Demonstrate virtual memory concepts"""
        print("\n=== Virtual Memory Concepts ===")
        
        # Show process address space
        print("\n1. Process Address Space Layout:")
        maps = self.get_memory_maps()
        for i, mem_map in enumerate(maps[:10]):  # Show first 10 entries
            print(f"  {mem_map.get('start', 'N/A')}-{mem_map.get('end', 'N/A')} "
                  f"{mem_map.get('perms', 'N/A')} {mem_map.get('path', '')}")
        
        if len(maps) > 10:
            print(f"  ... and {len(maps) - 10} more entries")
        
        # Demonstrate memory-mapped file (concept)
        print("\n2. Memory-Mapped File Concept:")
        try:
            # Create a temporary file and map it to memory
            with open('temp_mmap.bin', 'wb') as f:
                # Write some data
                data = b'This is a memory-mapped file demonstration' * 1000
                f.write(data)
            
            # Memory map the file
            with open('temp_mmap.bin', 'r+b') as f:
                # Memory-map the file
                mmapped = mmap.mmap(f.fileno(), 0)
                
                print(f"  File size: {len(data)} bytes")
                print(f"  Mapped size: {mmapped.size()} bytes")
                
                # Read from memory map
                print(f"  First 50 bytes: {mmapped[:50]}")
                
                # Modify through memory map
                mmapped[0:5] = b'THESE'
                print(f"  Modified first 5 bytes: {mmapped[:10]}")
                
                mmapped.close()
            
            # Clean up
            os.remove('temp_mmap.bin')
            print("  Temporary file cleaned up")
            
        except Exception as e:
            print(f"  Note: Memory-mapped file demo skipped: {e}")
        
        # Show shared library concept
        print("\n3. Shared Libraries (Concept):")
        print("  - Multiple processes can share the same library code in memory")
        print("  - Each process has its own data segment")
        print("  - Saves physical memory when multiple instances run")
    
    def demonstrate_paging_concept(self):
        """Demonstrate paging concept with a simple simulation"""
        print("\n=== Paging Concept Simulation ===")
        
        # Simple page table simulation
        page_size = 4096  # 4KB
        virtual_pages = 16
        physical_frames = 8
        
        print(f"Page Size: {page_size} bytes (4KB)")
        print(f"Virtual Address Space: {virtual_pages} pages")
        print(f"Physical Memory: {physical_frames} frames")
        
        # Simulate page table
        page_table = {}
        for i in range(virtual_pages):
            # Random mapping or not mapped
            import random
            if i < physical_frames:
                page_table[i] = i  # First 8 pages mapped to frames 0-7
            else:
                page_table[i] = None  # Not in memory
        
        print("\nPage Table (simplified):")
        print("Virtual Page -> Physical Frame")
        for vpage, pframe in page_table.items():
            status = f"Frame {pframe}" if pframe is not None else "Not in memory (page fault)"
            print(f"  Page {vpage:2d} -> {status}")
        
        # Simulate address translation
        print("\nAddress Translation Example:")
        virtual_address = 0x1234
        page_number = virtual_address // page_size
        offset = virtual_address % page_size
        
        print(f"Virtual Address: 0x{virtual_address:04x}")
        print(f"  Page Number: {page_number}")
        print(f"  Offset: 0x{offset:04x}")
        
        if page_number in page_table and page_table[page_number] is not None:
            physical_frame = page_table[page_number]
            physical_address = (physical_frame * page_size) + offset
            print(f"  Physical Address: 0x{physical_address:04x}")
        else:
            print("  PAGE FAULT: Page not in memory!")
    
    def memory_pressure_test(self):
        """Create memory pressure to observe swapping behavior"""
        print("\n=== Memory Pressure Test ===")
        print("Warning: This may slow down your system!")
        response = input("Continue? (y/n): ")
        
        if response.lower() != 'y':
            print("Test skipped")
            return
        
        try:
            # Get available memory
            mem = psutil.virtual_memory()
            available_mb = mem.available // (1024 * 1024)
            test_size = min(available_mb // 2, 512)  # Use half of available or 512MB max
            
            print(f"Available memory: {available_mb} MB")
            print(f"Allocating: {test_size} MB")
            
            # Allocate memory in chunks
            chunks = []
            chunk_size = 10  # MB per chunk
            
            for i in range(0, test_size, chunk_size):
                try:
                    # Allocate chunk
                    chunk = ' ' * (chunk_size * 1024 * 1024)  # Simple string allocation
                    chunks.append(chunk)
                    
                    # Check memory usage
                    mem = psutil.virtual_memory()
                    swap = psutil.swap_memory()
                    
                    print(f"Allocated: {(i + chunk_size)}/{test_size} MB | "
                          f"RAM used: {mem.percent}% | "
                          f"Swap used: {swap.percent}%")
                    
                    time.sleep(0.5)
                    
                except MemoryError:
                    print("MemoryError: Cannot allocate more memory!")
                    break
            
            print("\nHolding allocated memory for 3 seconds...")
            time.sleep(3)
            
            # Release memory
            print("Releasing memory...")
            chunks.clear()
            import gc
            gc.collect()
            
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            print(f"After release - RAM used: {mem.percent}% | Swap used: {swap.percent}%")
            
        except Exception as e:
            print(f"Error during memory pressure test: {e}")

def main():
    """Main function to demonstrate memory management"""
    mm = MemoryManager()
    
    # Display system memory info
    print("=== System Memory Information ===")
    sys_mem = mm.get_system_memory_info()
    for key, value in sys_mem.items():
        print(f"{key}: {value}")
    
    # Display current process memory info
    print("\n=== Current Process Memory Information ===")
    proc_mem = mm.get_process_memory_info()
    for key, value in proc_mem.items():
        print(f"{key}: {value}")
    
    # Demonstrate virtual memory concepts
    mm.demonstrate_virtual_memory_concepts()
    
    # Demonstrate paging concept
    mm.demonstrate_paging_concept()
    
    # Monitor memory changes
    mm.monitor_memory_changes(interval=0.5, duration=5)
    
    # Run OS-specific commands
    if mm.system == "Linux":
        mm.run_linux_memory_commands()
    elif mm.system == "Windows":
        mm.run_windows_memory_commands()
    
    # Simulate memory allocation (small size for safety)
    mm.simulate_memory_allocation(size_mb=50)
    
    # Ask before running memory pressure test
    print("\n" + "="*50)
    print("Additional demonstrations available:")
    print("1. Memory pressure test (may slow system)")
    print("2. View detailed memory maps")
    
    choice = input("\nSelect option (1, 2, or Enter to skip): ")
    
    if choice == "1":
        mm.memory_pressure_test()
    elif choice == "2":
        print("\n=== Detailed Memory Maps ===")
        maps = mm.get_memory_maps()
        for i, mem_map in enumerate(maps[:20]):  # Limit output
            print(f"{i+1:3d}. {mem_map}")
    
    print("\n=== Memory Management Demo Complete ===")

if __name__ == "__main__":
    # Check for psutil, install if not available
    try:
        import psutil
    except ImportError:
        print("Installing required package: psutil")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    main() 
