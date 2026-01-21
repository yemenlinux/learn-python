#!/usr/bin/env python3
"""
Page Table Structure Simulations
Illustrating:
1. Hierarchical Paging (Multi-level Paging)
2. Hashed Page Tables
3. Inverted Page Tables
"""

import hashlib
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class MemoryAccess:
    """Represents a memory access request"""
    pid: int
    virtual_address: int
    operation: str  # 'read' or 'write'

class HierarchicalPaging:
    """
    Simulates Hierarchical (Multi-level) Paging
    Implements a 2-level page table for 32-bit address space
    """
    
    def __init__(self, page_size_kb: int = 4, outer_bits: int = 10, inner_bits: int = 10):
        """
        Args:
            page_size_kb: Page size in KB (default 4KB)
            outer_bits: Bits for outer page table (default 10 bits → 1024 entries)
            inner_bits: Bits for inner page table (default 10 bits → 1024 entries)
        """
        self.page_size = page_size_kb * 1024  # Convert to bytes
        self.outer_bits = outer_bits
        self.inner_bits = inner_bits
        self.offset_bits = 12  # 4KB page = 2^12 bytes
        
        # Validate bit distribution (should total 32 for 32-bit address space)
        total_bits = outer_bits + inner_bits + self.offset_bits
        if total_bits != 32:
            print(f"Warning: Bit distribution doesn't match 32-bit address space")
            print(f"Outer: {outer_bits}, Inner: {inner_bits}, Offset: {self.offset_bits} = {total_bits} bits")
        
        # Outer page table: points to inner page tables
        self.outer_page_table = {}
        
        # Inner page tables: store actual frame mappings
        self.inner_page_tables = {}
        
        # Physical memory frames (simulated)
        self.physical_frames = {}
        self.next_frame = 0
        self.frame_count = 2**20  # 1 million frames (4GB physical memory with 4KB frames)
        
        # Statistics
        self.access_count = 0
        self.page_faults = 0
        self.tlb_hits = 0
        
        # TLB simulation (small cache of recent translations)
        self.tlb = {}
        self.tlb_size = 64
        
        print(f"=== Hierarchical Paging Simulation ===")
        print(f"Page Size: {page_size_kb} KB ({self.page_size} bytes)")
        print(f"Outer Page Table: {2**outer_bits} entries")
        print(f"Inner Page Table: {2**inner_bits} entries")
        print(f"Virtual Address Bits: Outer={outer_bits}, Inner={inner_bits}, Offset={self.offset_bits}")
        print()
    
    def _split_virtual_address(self, virtual_address: int) -> Tuple[int, int, int]:
        """Split 32-bit virtual address into outer, inner, and offset"""
        # Create masks
        offset_mask = (1 << self.offset_bits) - 1
        inner_mask = (1 << self.inner_bits) - 1
        outer_mask = (1 << self.outer_bits) - 1
        
        # Extract bits
        offset = virtual_address & offset_mask
        inner = (virtual_address >> self.offset_bits) & inner_mask
        outer = (virtual_address >> (self.offset_bits + self.inner_bits)) & outer_mask
        
        return outer, inner, offset
    
    def _allocate_frame(self) -> Optional[int]:
        """Allocate a physical frame"""
        if self.next_frame < self.frame_count:
            frame = self.next_frame
            self.next_frame += 1
            return frame
        return None
    
    def translate_address(self, virtual_address: int, pid: int) -> Tuple[bool, Optional[int], str]:
        """
        Translate virtual address to physical address using 2-level page tables
        Returns: (success, physical_address, description)
        """
        self.access_count += 1
        
        # Check TLB first
        tlb_key = (pid, virtual_address >> self.offset_bits)  # Page number as key
        if tlb_key in self.tlb:
            self.tlb_hits += 1
            frame = self.tlb[tlb_key]
            offset = virtual_address & ((1 << self.offset_bits) - 1)
            physical_address = (frame << self.offset_bits) | offset
            return True, physical_address, "TLB hit"
        
        # Split virtual address
        outer, inner, offset = self._split_virtual_address(virtual_address)
        
        # Lookup in outer page table
        if pid not in self.outer_page_table:
            # Outer page table doesn't exist for this process
            self.page_faults += 1
            return False, None, f"Page fault: Outer page table not found for process {pid}"
        
        outer_entry = self.outer_page_table[pid]
        if outer not in outer_entry:
            # Inner page table not present
            self.page_faults += 1
            return False, None, f"Page fault: Inner page table {outer} not present"
        
        # Get inner page table
        inner_table_addr = outer_entry[outer]
        if inner_table_addr not in self.inner_page_tables:
            # Inner page table not loaded
            self.page_faults += 1
            return False, None, f"Page fault: Inner page table not in memory"
        
        # Lookup in inner page table
        inner_table = self.inner_page_tables[inner_table_addr]
        if inner not in inner_table:
            # Page not present
            self.page_faults += 1
            return False, None, f"Page fault: Page {inner} not in inner table"
        
        # Get frame number
        frame = inner_table[inner]
        
        # Update TLB (with simple FIFO replacement)
        if len(self.tlb) >= self.tlb_size:
            # Remove oldest entry
            oldest_key = next(iter(self.tlb))
            del self.tlb[oldest_key]
        self.tlb[tlb_key] = frame
        
        # Calculate physical address
        physical_address = (frame << self.offset_bits) | offset
        
        return True, physical_address, f"Translation successful: Outer={outer}, Inner={inner}, Frame={frame}"
    
    def create_process(self, pid: int, pages_to_allocate: int = 10) -> None:
        """Initialize page tables for a new process"""
        # Create outer page table for process
        self.outer_page_table[pid] = {}
        
        # Allocate one inner page table initially
        inner_table_addr = len(self.inner_page_tables)
        self.inner_page_tables[inner_table_addr] = {}
        
        # Map first outer entry to this inner table
        self.outer_page_table[pid][0] = inner_table_addr
        
        # Allocate some pages in the inner table
        for i in range(min(pages_to_allocate, 2**self.inner_bits)):
            frame = self._allocate_frame()
            if frame is not None:
                self.inner_page_tables[inner_table_addr][i] = frame
                self.physical_frames[frame] = (pid, i)  # Track frame ownership
        
        print(f"Created process {pid} with {pages_to_allocate} pages allocated")
    
    def print_stats(self) -> None:
        """Print simulation statistics"""
        print(f"\n=== Hierarchical Paging Statistics ===")
        print(f"Total memory accesses: {self.access_count}")
        print(f"Page faults: {self.page_faults}")
        print(f"TLB hits: {self.tlb_hits}")
        if self.access_count > 0:
            print(f"TLB hit rate: {(self.tlb_hits/self.access_count)*100:.2f}%")
            print(f"Page fault rate: {(self.page_faults/self.access_count)*100:.2f}%")
        print(f"Memory used: {self.next_frame} frames ({self.next_frame * self.page_size / (1024**2):.2f} MB)")
        print(f"Outer page tables: {len(self.outer_page_table)}")
        print(f"Inner page tables: {len(self.inner_page_tables)}")

class HashedPageTable:
    """
    Simulates Hashed Page Tables
    Uses hash table with chaining for collision resolution
    """
    
    def __init__(self, page_size_kb: int = 4, hash_table_size: int = 1024):
        """
        Args:
            page_size_kb: Page size in KB (default 4KB)
            hash_table_size: Size of the hash table (number of buckets)
        """
        self.page_size = page_size_kb * 1024
        self.hash_table_size = hash_table_size
        
        # Hash table: array of linked lists (simulated as lists of dicts)
        self.hash_table = [[] for _ in range(hash_table_size)]
        
        # Physical memory frames
        self.physical_frames = {}
        self.next_frame = 0
        self.frame_count = 2**20  # 1 million frames
        
        # Statistics
        self.access_count = 0
        self.page_faults = 0
        self.hash_collisions = 0
        
        print(f"\n=== Hashed Page Table Simulation ===")
        print(f"Page Size: {page_size_kb} KB ({self.page_size} bytes)")
        print(f"Hash Table Size: {hash_table_size} buckets")
        print(f"Collision Resolution: Chaining")
        print()
    
    def _hash_function(self, pid: int, virtual_page: int) -> int:
        """Hash function for (pid, virtual_page) pair"""
        # Combine pid and virtual page
        key = f"{pid}:{virtual_page}"
        
        # Use SHA-256 hash and mod to table size
        hash_bytes = hashlib.sha256(key.encode()).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        
        return hash_int % self.hash_table_size
    
    def _allocate_frame(self) -> Optional[int]:
        """Allocate a physical frame"""
        if self.next_frame < self.frame_count:
            frame = self.next_frame
            self.next_frame += 1
            return frame
        return None
    
    def translate_address(self, virtual_address: int, pid: int) -> Tuple[bool, Optional[int], str]:
        """
        Translate virtual address using hashed page table
        Returns: (success, physical_address, description)
        """
        self.access_count += 1
        
        # Extract page number and offset
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        # Calculate hash
        hash_index = self._hash_function(pid, page_number)
        bucket = self.hash_table[hash_index]
        
        # Search in bucket (linked list)
        entries_searched = 0
        for entry in bucket:
            entries_searched += 1
            if entry['pid'] == pid and entry['virtual_page'] == page_number:
                # Found the mapping
                frame = entry['frame']
                physical_address = (frame * self.page_size) + offset
                
                # Move to front (LRU approximation)
                if entries_searched > 1:
                    bucket.remove(entry)
                    bucket.insert(0, entry)
                
                return True, physical_address, f"Found in hash bucket {hash_index} after searching {entries_searched} entries"
        
        # Page not found - page fault
        self.page_faults += 1
        
        # Check for collisions
        if len(bucket) > 0:
            self.hash_collisions += 1
        
        return False, None, f"Page fault: Page {page_number} not found in hash bucket {hash_index}"
    
    def insert_mapping(self, pid: int, virtual_page: int, frame: Optional[int] = None) -> None:
        """Insert a new page table entry"""
        if frame is None:
            frame = self._allocate_frame()
            if frame is None:
                print(f"Error: No free frames available")
                return
        
        # Create entry
        entry = {
            'pid': pid,
            'virtual_page': virtual_page,
            'frame': frame
        }
        
        # Calculate hash
        hash_index = self._hash_function(pid, virtual_page)
        
        # Add to bucket (at front for LRU)
        self.hash_table[hash_index].insert(0, entry)
        
        # Track frame ownership
        self.physical_frames[frame] = (pid, virtual_page)
    
    def simulate_collisions(self, num_entries: int = 1000) -> None:
        """Simulate hash table behavior with many entries"""
        print(f"Simulating {num_entries} random page table entries...")
        
        bucket_sizes = defaultdict(int)
        for i in range(num_entries):
            pid = random.randint(1, 10)
            virtual_page = random.randint(0, 1000000)
            self.insert_mapping(pid, virtual_page)
            
            # Track bucket sizes
            hash_index = self._hash_function(pid, virtual_page)
            bucket_sizes[hash_index] += 1
        
        # Analyze distribution
        max_bucket = max(bucket_sizes.values()) if bucket_sizes else 0
        avg_bucket = sum(bucket_sizes.values()) / len(bucket_sizes) if bucket_sizes else 0
        
        print(f"Hash table analysis:")
        print(f"  Total entries: {num_entries}")
        print(f"  Max bucket size: {max_bucket}")
        print(f"  Average bucket size: {avg_bucket:.2f}")
        print(f"  Empty buckets: {self.hash_table_size - len(bucket_sizes)}")
    
    def print_stats(self) -> None:
        """Print simulation statistics"""
        print(f"\n=== Hashed Page Table Statistics ===")
        print(f"Total memory accesses: {self.access_count}")
        print(f"Page faults: {self.page_faults}")
        
        # Calculate bucket statistics
        non_empty_buckets = sum(1 for bucket in self.hash_table if len(bucket) > 0)
        total_entries = sum(len(bucket) for bucket in self.hash_table)
        
        if non_empty_buckets > 0:
            avg_bucket_size = total_entries / non_empty_buckets
            print(f"Non-empty buckets: {non_empty_buckets}/{self.hash_table_size}")
            print(f"Average chain length: {avg_bucket_size:.2f}")
        
        print(f"Hash collisions: {self.hash_collisions}")
        print(f"Memory used: {self.next_frame} frames")

class InvertedPageTable:
    """
    Simulates Inverted Page Tables
    One entry per physical frame, indexed by frame number
    """
    
    def __init__(self, page_size_kb: int = 4, physical_memory_mb: int = 256):
        """
        Args:
            page_size_kb: Page size in KB (default 4KB)
            physical_memory_mb: Physical memory size in MB (default 256MB)
        """
        self.page_size = page_size_kb * 1024
        self.physical_memory_bytes = physical_memory_mb * 1024 * 1024
        
        # Calculate number of frames
        self.frame_count = self.physical_memory_bytes // self.page_size
        
        # Inverted page table: array indexed by frame number
        # Each entry contains (pid, virtual_page) or None if free
        self.inverted_table = [None] * self.frame_count
        
        # Hash table for quick lookup (pid, virtual_page) -> frame
        self.lookup_hash = {}
        
        # Free frame list
        self.free_frames = list(range(self.frame_count))
        random.shuffle(self.free_frames)  # Randomize for simulation
        
        # Statistics
        self.access_count = 0
        self.page_faults = 0
        self.hash_lookups = 0
        self.linear_searches = 0
        
        print(f"\n=== Inverted Page Table Simulation ===")
        print(f"Page Size: {page_size_kb} KB ({self.page_size} bytes)")
        print(f"Physical Memory: {physical_memory_mb} MB")
        print(f"Number of frames: {self.frame_count}")
        print(f"Inverted Table Size: {self.frame_count} entries (one per frame)")
        print()
    
    def _hash_function(self, pid: int, virtual_page: int) -> int:
        """Hash function for (pid, virtual_page) pair"""
        key = f"{pid}:{virtual_page}"
        hash_bytes = hashlib.md5(key.encode()).digest()
        hash_int = int.from_bytes(hash_bytes, 'big')
        return hash_int % 1024  # Fixed size for demonstration
    
    def _allocate_frame(self) -> Optional[int]:
        """Allocate a free frame"""
        if self.free_frames:
            return self.free_frames.pop()
        return None
    
    def translate_address(self, virtual_address: int, pid: int) -> Tuple[bool, Optional[int], str]:
        """
        Translate virtual address using inverted page table
        Returns: (success, physical_address, description)
        """
        self.access_count += 1
        
        # Extract page number and offset
        page_number = virtual_address // self.page_size
        offset = virtual_address % self.page_size
        
        # Try hash lookup first (real systems use this)
        self.hash_lookups += 1
        hash_key = (pid, page_number)
        
        if hash_key in self.lookup_hash:
            frame = self.lookup_hash[hash_key]
            physical_address = (frame * self.page_size) + offset
            return True, physical_address, f"Found via hash lookup: frame {frame}"
        
        # Hash miss - need to search inverted table
        # In real systems, this would use a hardware hash table
        # Here we simulate with linear search for demonstration
        search_steps = 0
        for frame in range(self.frame_count):
            search_steps += 1
            entry = self.inverted_table[frame]
            if entry is not None and entry[0] == pid and entry[1] == page_number:
                # Found it
                physical_address = (frame * self.page_size) + offset
                
                # Update hash table for future lookups
                self.lookup_hash[hash_key] = frame
                
                self.linear_searches += search_steps
                return True, physical_address, f"Found after linear search of {search_steps} frames"
        
        # Page fault - not found
        self.page_faults += 1
        return False, None, f"Page fault: No frame contains (pid={pid}, page={page_number})"
    
    def map_page(self, pid: int, virtual_page: int) -> Tuple[bool, Optional[int]]:
        """Map a virtual page to a physical frame"""
        # Check if already mapped
        for frame in range(self.frame_count):
            entry = self.inverted_table[frame]
            if entry is not None and entry[0] == pid and entry[1] == virtual_page:
                return True, frame  # Already mapped
        
        # Allocate new frame
        frame = self._allocate_frame()
        if frame is None:
            return False, None  # No free frames
        
        # Update inverted table
        self.inverted_table[frame] = (pid, virtual_page)
        
        # Update hash table
        self.lookup_hash[(pid, virtual_page)] = frame
        
        return True, frame
    
    def simulate_shared_memory(self):
        """Demonstrate shared memory with inverted page tables"""
        print("Demonstrating shared memory...")
        
        # Map same physical frame to two different processes
        shared_frame = self._allocate_frame()
        if shared_frame is None:
            print("  No free frames for shared memory demo")
            return
        
        # Process 1 maps virtual page 100 to shared frame
        self.inverted_table[shared_frame] = (1, 100)
        self.lookup_hash[(1, 100)] = shared_frame
        
        # Process 2 maps virtual page 200 to same shared frame
        self.inverted_table[shared_frame] = (2, 200)  # Overwrites! This is a problem
        # Actually, we need a different structure to support sharing
        # Real systems handle this differently
        
        print(f"  Frame {shared_frame} is shared (conceptually)")
        print("  Note: Actual sharing requires additional data structures")
    
    def print_table_sample(self, num_samples: int = 10):
        """Print a sample of the inverted page table"""
        print(f"\nSample of Inverted Page Table (first {num_samples} entries):")
        print("Frame | PID | Virtual Page")
        print("-" * 30)
        
        for frame in range(min(num_samples, self.frame_count)):
            entry = self.inverted_table[frame]
            if entry:
                pid, vpage = entry
                print(f"{frame:5d} | {pid:3d} | {vpage:12d}")
            else:
                print(f"{frame:5d} | FREE |")
    
    def print_stats(self):
        """Print simulation statistics"""
        print(f"\n=== Inverted Page Table Statistics ===")
        print(f"Total memory accesses: {self.access_count}")
        print(f"Page faults: {self.page_faults}")
        
        # Calculate occupancy
        used_frames = sum(1 for entry in self.inverted_table if entry is not None)
        occupancy = (used_frames / self.frame_count) * 100
        
        print(f"Frames used: {used_frames}/{self.frame_count} ({occupancy:.1f}%)")
        print(f"Hash lookups: {self.hash_lookups}")
        if self.linear_searches > 0:
            avg_search = self.linear_searches / (self.access_count - self.hash_lookups) if self.access_count > self.hash_lookups else 0
            print(f"Average linear search steps: {avg_search:.1f}")

def simulate_hierarchical_paging():
    """Demo for hierarchical paging"""
    print("\n" + "="*70)
    print("HIERARCHICAL PAGING DEMONSTRATION")
    print("="*70)
    
    hp = HierarchicalPaging(page_size_kb=4, outer_bits=10, inner_bits=10)
    
    # Create processes
    hp.create_process(pid=1, pages_to_allocate=50)
    hp.create_process(pid=2, pages_to_allocate=30)
    
    # Simulate some memory accesses
    print("\nSimulating memory accesses...")
    
    # Process 1 accesses
    for i in range(20):
        va = random.randint(0, 0xFFFFF) << 12  # Random page, keep offset 0 for simplicity
        success, pa, desc = hp.translate_address(va, pid=1)
        if i < 3:  # Show first few translations
            print(f"Process 1: VA=0x{va:08x} -> {desc}")
    
    # Process 2 accesses
    for i in range(15):
        va = random.randint(0, 0xFFFFF) << 12
        success, pa, desc = hp.translate_address(va, pid=2)
        if i < 3:
            print(f"Process 2: VA=0x{va:08x} -> {desc}")
    
    # Show address breakdown for a specific address
    print("\nExample address breakdown:")
    example_va = 0x12345678
    outer, inner, offset = hp._split_virtual_address(example_va)
    print(f"Virtual Address: 0x{example_va:08x}")
    print(f"  Outer page index: {outer} (0x{outer:03x})")
    print(f"  Inner page index: {inner} (0x{inner:03x})")
    print(f"  Offset: {offset} (0x{offset:03x})")
    
    hp.print_stats()

def simulate_hashed_page_table():
    """Demo for hashed page tables"""
    print("\n" + "="*70)
    print("HASHED PAGE TABLE DEMONSTRATION")
    print("="*70)
    
    hpt = HashedPageTable(page_size_kb=4, hash_table_size=512)
    
    # Simulate hash collisions
    hpt.simulate_collisions(num_entries=2000)
    
    # Insert some mappings
    print("\nInserting page table entries...")
    for i in range(100):
        pid = random.randint(1, 5)
        virtual_page = random.randint(0, 10000)
        hpt.insert_mapping(pid, virtual_page)
    
    # Simulate accesses
    print("\nSimulating memory accesses...")
    for i in range(50):
        pid = random.randint(1, 5)
        virtual_page = random.randint(0, 10000)
        va = virtual_page * hpt.page_size + random.randint(0, hpt.page_size-1)
        
        success, pa, desc = hpt.translate_address(va, pid)
        if i < 5:
            print(f"PID {pid}: VA=0x{va:08x} -> {desc}")
    
    hpt.print_stats()

def simulate_inverted_page_table():
    """Demo for inverted page tables"""
    print("\n" + "="*70)
    print("INVERTED PAGE TABLE DEMONSTRATION")
    print("="*70)
    
    ipt = InvertedPageTable(page_size_kb=4, physical_memory_mb=128)
    
    # Map some pages
    print("Mapping virtual pages to physical frames...")
    mappings_created = 0
    for pid in range(1, 4):
        for page in range(50):
            success, frame = ipt.map_page(pid, page)
            if success:
                mappings_created += 1
    
    print(f"Created {mappings_created} page mappings")
    
    # Show table sample
    ipt.print_table_sample(num_samples=15)
    
    # Simulate shared memory
    ipt.simulate_shared_memory()
    
    # Simulate accesses
    print("\nSimulating memory accesses...")
    for i in range(30):
        pid = random.randint(1, 3)
        virtual_page = random.randint(0, 49)
        va = virtual_page * ipt.page_size + random.randint(0, ipt.page_size-1)
        
        success, pa, desc = ipt.translate_address(va, pid)
        if i < 5:
            status = "SUCCESS" if success else "PAGE FAULT"
            print(f"PID {pid}: VA=0x{va:08x} -> {status}: {desc}")
    
    ipt.print_stats()

def comparison_table():
    """Create a comparison table of different page table structures"""
    print("\n" + "="*70)
    print("PAGE TABLE STRUCTURE COMPARISON")
    print("="*70)
    
    comparison = [
        ["Feature", "Hierarchical Paging", "Hashed Page Tables", "Inverted Page Tables"],
        ["Memory Usage", "High (multiple levels)", "Moderate (hash table + chains)", "Low (one entry per frame)"],
        ["Lookup Speed", "2+ memory accesses", "1-2 accesses (good hash)", "1 access (with hash), O(n) worst"],
        ["Scalability", "Good for 32-bit", "Excellent for 64-bit", "Excellent (scales with physical memory)"],
        ["Complexity", "Moderate", "High (hash collisions)", "High (shared memory tricky)"],
        ["Shared Memory", "Easy (share frames)", "Moderate", "Difficult (needs extra structures)"],
        ["Context Switch", "Change page table base", "Change hash table pointer", "No change (global table)"],
        ["Common Use", "32-bit x86 (2-level)", "64-bit systems", "Some 64-bit architectures"],
    ]
    
    # Print table
    col_widths = [max(len(str(row[i])) for row in comparison) for i in range(len(comparison[0]))]
    
    for i, row in enumerate(comparison):
        formatted_row = " | ".join(str(item).ljust(col_widths[j]) for j, item in enumerate(row))
        print(formatted_row)
        if i == 0:
            print("-" * sum(col_widths + [3 * len(col_widths)]))

def main():
    """Main function to run all demonstrations"""
    print("Page Table Structure Simulations")
    print("Illustrating memory management concepts from Operating Systems")
    print()
    
    # Run all demonstrations
    simulate_hierarchical_paging()
    simulate_hashed_page_table()
    simulate_inverted_page_table()
    comparison_table()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
1. HIERARCHICAL PAGING (Multi-level):
   - Uses multiple levels of page tables
   - Good for 32-bit address spaces
   - Example: x86 uses 2-level (32-bit) or 4-level (64-bit) paging
   - Each level reduces the size of page tables in memory

2. HASHED PAGE TABLES:
   - Uses hash table to map virtual to physical addresses
   - Excellent for sparse address spaces (64-bit)
   - Handles collisions with chaining
   - Used in PowerPC, SPARC, and some x86-64 implementations

3. INVERTED PAGE TABLES:
   - One entry per physical frame (not per virtual page)
   - Scales with physical memory, not virtual address space
   - Requires searching or hashing to find mappings
   - Used in some 64-bit architectures (HP PA-RISC, IBM AS/400)
   - Shared memory requires additional data structures
""")

if __name__ == "__main__":
    main() 
