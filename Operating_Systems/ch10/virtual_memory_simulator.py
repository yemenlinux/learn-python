"""
Virtual Memory Simulator
=======================
This program demonstrates key virtual memory concepts from the lecture:
1. Demand Paging
2. Page Replacement Algorithms
3. Copy-on-Write
4. Frame Allocation
5. Thrashing
6. Working Set Model
7. Buddy System
8. Slab Allocation
9. Performance Analysis
"""

import collections
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Deque
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np

class PageTableEntry:
    """Represents a page table entry with valid/invalid bit and other metadata"""
    def __init__(self, page_number: int):
        self.page_number = page_number
        self.valid = False  # v/i bit: False = invalid (not in memory)
        self.referenced = False  # Reference bit for clock algorithm
        self.modified = False  # Dirty bit
        self.frame_number = None
        self.last_access_time = 0
        self.access_count = 0
    
    def __str__(self):
        status = "v" if self.valid else "i"
        ref = "R" if self.referenced else "-"
        mod = "M" if self.modified else "-"
        return f"Page {self.page_number}: [{status}] Frame: {self.frame_number} {ref}{mod}"

class PageFault(Exception):
    """Exception raised when a page fault occurs"""
    pass

class MemoryManager:
    """Base class for memory management"""
    
    def __init__(self, total_frames: int):
        self.total_frames = total_frames
        self.free_frames = list(range(total_frames))
        self.allocated_frames = {}  # frame -> PageTableEntry
        self.page_faults = 0
        self.memory_accesses = 0
        
    def allocate_frame(self, page: PageTableEntry) -> int:
        """Allocate a free frame to a page"""
        if not self.free_frames:
            raise MemoryError("No free frames available")
        
        frame = self.free_frames.pop(0)
        self.allocated_frames[frame] = page
        page.frame_number = frame
        page.valid = True
        return frame
    
    def free_frame(self, frame: int):
        """Free a frame and return it to the free list"""
        if frame in self.allocated_frames:
            page = self.allocated_frames[frame]
            page.valid = False
            page.frame_number = None
            del self.allocated_frames[frame]
        self.free_frames.append(frame)
        self.free_frames.sort()

class DemandPagingSimulator(MemoryManager):
    """Simulates demand paging with various replacement algorithms"""
    
    class ReplacementAlgorithm(Enum):
        FIFO = "FIFO"
        OPTIMAL = "Optimal"
        LRU = "LRU"
        CLOCK = "Clock"
        LFU = "LFU"
        MFU = "MFU"
    
    def __init__(self, total_frames: int, algorithm: ReplacementAlgorithm):
        super().__init__(total_frames)
        self.algorithm = algorithm
        self.page_table: Dict[int, PageTableEntry] = {}
        self.access_history = []
        self.fifo_queue: Deque[int] = collections.deque()  # Store page numbers
        self.lru_counter = 0
        self.clock_hand = 0
        
    def access_page(self, page_number: int, is_write: bool = False):
        """Simulate accessing a page (read or write)"""
        self.memory_accesses += 1
        
        # Get or create page table entry
        if page_number not in self.page_table:
            self.page_table[page_number] = PageTableEntry(page_number)
        
        page = self.page_table[page_number]
        page.last_access_time = self.lru_counter
        page.access_count += 1
        page.referenced = True
        
        if is_write:
            page.modified = True
        
        # Check if page is in memory
        if not page.valid:
            self.handle_page_fault(page)
        else:
            print(f"Page {page_number}: Hit")
            # Update FIFO queue if using FIFO (only for pages already in queue)
            if self.algorithm == self.ReplacementAlgorithm.FIFO and page_number in self.fifo_queue:
                # Just update reference, but don't change position (FIFO doesn't change on hit)
                pass
    
    def handle_page_fault(self, page: PageTableEntry):
        """Handle a page fault"""
        self.page_faults += 1
        print(f"Page {page.page_number}: Fault #{self.page_faults}")
        
        try:
            # Try to allocate a free frame
            frame = self.allocate_frame(page)
            print(f"  Allocated frame {frame} to page {page.page_number}")
            # Add to FIFO queue if using FIFO
            if self.algorithm == self.ReplacementAlgorithm.FIFO:
                self.fifo_queue.append(page.page_number)
        except MemoryError:
            # No free frames, need page replacement
            print(f"  No free frames, running {self.algorithm.value} replacement")
            victim_page = self.select_victim()
            self.replace_page(victim_page, page)
    
    def select_victim(self) -> PageTableEntry:
        """Select a victim page based on the replacement algorithm"""
        if self.algorithm == self.ReplacementAlgorithm.FIFO:
            return self.fifo_replacement()
        elif self.algorithm == self.ReplacementAlgorithm.OPTIMAL:
            return self.optimal_replacement()
        elif self.algorithm == self.ReplacementAlgorithm.LRU:
            return self.lru_replacement()
        elif self.algorithm == self.ReplacementAlgorithm.CLOCK:
            return self.clock_replacement()
        elif self.algorithm == self.ReplacementAlgorithm.LFU:
            return self.lfu_replacement()
        elif self.algorithm == self.ReplacementAlgorithm.MFU:
            return self.mfu_replacement()
        
        return list(self.allocated_frames.values())[0]
    
    def fifo_replacement(self) -> PageTableEntry:
        """First-In-First-Out replacement"""
        if not self.fifo_queue:
            # Initialize FIFO queue with current pages in memory
            for frame, page in self.allocated_frames.items():
                self.fifo_queue.append(page.page_number)
        
        # Get the oldest page (first in)
        victim_page_number = self.fifo_queue.popleft()
        victim_page = self.page_table[victim_page_number]
        return victim_page
    
    def optimal_replacement(self) -> PageTableEntry:
        """Optimal page replacement (requires future knowledge)"""
        # This is a simulation - we'll use the remaining access history
        future_accesses = self.access_history.copy()
        
        # Find page that won't be used for the longest time
        max_future_distance = -1
        victim_page = None
        
        current_pages = list(self.allocated_frames.values())
        
        # Check each page currently in memory
        for page in current_pages:
            try:
                # Find next access of this page in future
                next_use = future_accesses.index(page.page_number)
                if next_use > max_future_distance:
                    max_future_distance = next_use
                    victim_page = page
            except ValueError:
                # Page not accessed again - this is the best victim
                return page
        
        return victim_page if victim_page else current_pages[0]
    
    def lru_replacement(self) -> PageTableEntry:
        """Least Recently Used replacement"""
        lru_page = None
        oldest_time = float('inf')
        
        for page in self.allocated_frames.values():
            if page.last_access_time < oldest_time:
                oldest_time = page.last_access_time
                lru_page = page
        
        return lru_page
    
    def clock_replacement(self) -> PageTableEntry:
        """Clock (Second Chance) replacement"""
        frames = list(self.allocated_frames.keys())
        
        # If no frames allocated, return None (shouldn't happen)
        if not frames:
            return None
            
        while True:
            frame = frames[self.clock_hand]
            page = self.allocated_frames[frame]
            
            if not page.referenced:
                # This is our victim
                self.clock_hand = (self.clock_hand + 1) % len(frames)
                return page
            
            # Give a second chance
            page.referenced = False
            self.clock_hand = (self.clock_hand + 1) % len(frames)
    
    def lfu_replacement(self) -> PageTableEntry:
        """Least Frequently Used replacement"""
        lfu_page = None
        min_accesses = float('inf')
        
        for page in self.allocated_frames.values():
            if page.access_count < min_accesses:
                min_accesses = page.access_count
                lfu_page = page
        
        return lfu_page
    
    def mfu_replacement(self) -> PageTableEntry:
        """Most Frequently Used replacement"""
        mfu_page = None
        max_accesses = -1
        
        for page in self.allocated_frames.values():
            if page.access_count > max_accesses:
                max_accesses = page.access_count
                mfu_page = page
        
        return mfu_page
    
    def replace_page(self, victim: PageTableEntry, new_page: PageTableEntry):
        """Replace a victim page with a new page"""
        if victim is None:
            return
            
        print(f"  Replacing page {victim.page_number} in frame {victim.frame_number}")
        
        # Write back if modified
        if victim.modified:
            print(f"  Writing page {victim.page_number} back to disk (dirty)")
        
        # Free the victim's frame
        self.free_frame(victim.frame_number)
        
        # Allocate frame to new page
        frame = self.allocate_frame(new_page)
        print(f"  Allocated frame {frame} to page {new_page.page_number}")
        
        # Update FIFO queue if using FIFO
        if self.algorithm == self.ReplacementAlgorithm.FIFO:
            self.fifo_queue.append(new_page.page_number)
    
    def run_simulation(self, reference_string: List[int], writes: Optional[List[bool]] = None):
        """Run a simulation with a given reference string"""
        print(f"\n{'='*60}")
        print(f"Running {self.algorithm.value} Algorithm with {self.total_frames} frames")
        print(f"Reference string: {reference_string}")
        print(f"{'='*60}")
        
        self.access_history = reference_string.copy()
        
        for i, page_num in enumerate(reference_string):
            is_write = writes[i] if writes and i < len(writes) else False
            print(f"\nAccess {i+1}: Page {page_num} ({'Write' if is_write else 'Read'})")
            self.access_page(page_num, is_write)
            self.lru_counter += 1
        
        self.print_statistics()
    
    def print_statistics(self):
        """Print simulation statistics"""
        print(f"\n{'='*60}")
        print("SIMULATION STATISTICS")
        print(f"{'='*60}")
        print(f"Total memory accesses: {self.memory_accesses}")
        print(f"Page faults: {self.page_faults}")
        
        if self.memory_accesses > 0:
            fault_rate = self.page_faults / self.memory_accesses
            print(f"Page fault rate: {fault_rate:.2%}")
            
            # Calculate Effective Access Time (simplified)
            memory_access_time = 200  # nanoseconds
            page_fault_service_time = 8_000_000  # nanoseconds (8ms)
            
            eat = (1 - fault_rate) * memory_access_time + \
                  fault_rate * page_fault_service_time
            
            print(f"Effective Access Time: {eat:.2f} ns")
            print(f"Slowdown factor: {eat / memory_access_time:.1f}x")
        
        print("\nFinal page table:")
        for page_num in sorted(self.page_table.keys()):
            print(f"  {self.page_table[page_num]}")

class CopyOnWriteSimulator:
    """Demonstrates Copy-on-Write (COW) mechanism"""
    
    def __init__(self):
        self.shared_pages = {}
        self.process_pages = {}
        
    def fork_process(self, parent_pid: int, child_pid: int):
        """Simulate fork() with COW"""
        print(f"\n{'='*60}")
        print(f"FORK: Creating child process {child_pid} from parent {parent_pid}")
        print(f"{'='*60}")
        
        # Initially, child shares all pages with parent
        self.process_pages[child_pid] = {}
        if parent_pid in self.process_pages:
            for page_num, info in self.process_pages[parent_pid].items():
                # Child gets references to same pages
                self.process_pages[child_pid][page_num] = info.copy()
                # Increment reference count
                if 'data_ptr' in info:
                    ptr = info['data_ptr']
                    if ptr in self.shared_pages:
                        self.shared_pages[ptr]['ref_count'] += 1
        
        print("Initial state: Child shares all pages with parent (COW)")
        self.print_memory_state()
    
    def write_to_page(self, pid: int, page_num: int, new_data: str):
        """Simulate a write to a COW page"""
        print(f"\nProcess {pid} writing to page {page_num}")
        
        if pid not in self.process_pages or page_num not in self.process_pages[pid]:
            print(f"  Page {page_num} not in process {pid}'s address space")
            return
        
        info = self.process_pages[pid][page_num]
        
        # Check if this is a shared page (has ref_count > 1)
        if 'data_ptr' in info:
            ptr = info['data_ptr']
            if ptr in self.shared_pages and self.shared_pages[ptr]['ref_count'] > 1:
                print(f"  Page {page_num} is shared (COW) - creating copy")
                
                # Decrement reference count of original
                self.shared_pages[ptr]['ref_count'] -= 1
                
                # Create new page with copy of data
                new_ptr = max(self.shared_pages.keys()) + 1 if self.shared_pages else 100
                self.shared_pages[new_ptr] = {
                    'data': self.shared_pages[ptr]['data'] + " -> " + new_data,
                    'ref_count': 1
                }
                
                # Update process to point to new page
                self.process_pages[pid][page_num] = {'data_ptr': new_ptr}
                
                print(f"  Created new page {new_ptr}")
                
                # Check if original page can be freed
                if self.shared_pages[ptr]['ref_count'] == 0:
                    print(f"  Original page {ptr} is no longer referenced - can be freed")
                    del self.shared_pages[ptr]
            else:
                # Not shared or ref_count is 1, can write directly
                print(f"  Page {page_num} is not shared - direct write")
                self.shared_pages[ptr]['data'] = new_data
        else:
            # No data_ptr, create new page
            new_ptr = max(self.shared_pages.keys()) + 1 if self.shared_pages else 100
            self.shared_pages[new_ptr] = {'data': new_data, 'ref_count': 1}
            self.process_pages[pid][page_num] = {'data_ptr': new_ptr}
            print(f"  Created new page {new_ptr} with data: '{new_data}'")
        
        self.print_memory_state()
    
    def print_memory_state(self):
        """Print current memory state"""
        print("\nCurrent Memory State:")
        print("Shared Pages:")
        for page_num, info in self.shared_pages.items():
            print(f"  Page {page_num}: data='{info['data']}', ref_count={info['ref_count']}")
        
        print("\nProcess Page Tables:")
        for pid, pages in self.process_pages.items():
            print(f"  Process {pid}:")
            for page_num, info in pages.items():
                if 'data_ptr' in info:
                    ptr = info['data_ptr']
                    ref_count = self.shared_pages[ptr]['ref_count'] if ptr in self.shared_pages else 0
                    status = "shared" if ref_count > 1 else "private"
                    print(f"    Virtual {page_num} -> Physical {ptr} ({status})")

class WorkingSetSimulator:
    """Demonstrates the Working Set model and thrashing"""
    
    def __init__(self, total_frames: int):
        self.total_frames = total_frames
        self.processes = {}
        self.time = 0
        self.delta = 4  # Working set window size
        
    def add_process(self, pid: int, locality_size: int):
        """Add a process with a specific locality size"""
        self.processes[pid] = {
            'locality': list(range(locality_size)),
            'current_locality': 0,
            'page_faults': 0,
            'working_set': set(),
            'access_history': collections.deque(maxlen=self.delta)
        }
    
    def simulate_access(self, pid: int):
        """Simulate a memory access for a process"""
        self.time += 1
        process = self.processes[pid]
        
        # Determine which page to access (within current locality)
        locality_pages = process['locality'][process['current_locality'] * 10: 
                                            (process['current_locality'] + 1) * 10]
        if not locality_pages:
            locality_pages = process['locality']
        
        page = random.choice(locality_pages)
        process['access_history'].append(page)
        
        # Update working set (last delta pages)
        process['working_set'] = set(process['access_history'])
        
        # Check if page is in working set
        if page not in process['working_set']:
            process['page_faults'] += 1
        
        # Occasionally change locality
        if random.random() < 0.1:
            process['current_locality'] = (process['current_locality'] + 1) % 3
        
        return page, len(process['working_set'])
    
    def detect_thrashing(self):
        """Detect if thrashing is occurring"""
        total_working_set = sum(len(p['working_set']) for p in self.processes.values())
        
        print(f"\nTime {self.time}: Total working set size = {total_working_set}")
        print(f"Available frames = {self.total_frames}")
        
        if total_working_set > self.total_frames:
            print("⚠️  THRASHING DETECTED! Σ Working Set > Total Memory")
            return True
        return False
    
    def run_simulation(self, steps: int = 20):
        """Run a working set simulation"""
        print(f"\n{'='*60}")
        print("WORKING SET SIMULATION")
        print(f"Δ (window size) = {self.delta}, Total frames = {self.total_frames}")
        print(f"{'='*60}")
        
        # Add some processes
        self.add_process(1, 30)  # Process with 30 pages
        self.add_process(2, 40)  # Process with 40 pages
        self.add_process(3, 20)  # Process with 20 pages
        
        for step in range(steps):
            print(f"\n--- Step {step + 1} ---")
            
            for pid in self.processes.keys():
                page, ws_size = self.simulate_access(pid)
                print(f"Process {pid}: accessed page {page}, WS size = {ws_size}")
            
            if self.detect_thrashing():
                print("Solution: Suspend one process to reduce memory pressure")
                break

class BuddySystemAllocator:
    """Implements the Buddy System for kernel memory allocation"""
    
    def __init__(self, total_memory: int):
        # Total memory must be power of 2
        self.total_memory = 1 << (total_memory - 1).bit_length()
        self.max_order = (self.total_memory - 1).bit_length()
        self.free_lists = [[] for _ in range(self.max_order + 1)]
        self.allocated_blocks = {}
        
        # Initialize with one big free block
        self.free_lists[self.max_order].append(0)
        print(f"Initialized Buddy System with {self.total_memory}KB total memory")
    
    def allocate(self, size: int) -> Optional[int]:
        """Allocate memory block of given size (in KB)"""
        # Round up to next power of 2
        order = (size - 1).bit_length()
        
        if order > self.max_order:
            print(f"Request too large: {size}KB > {self.total_memory}KB")
            return None
        
        # Find free block of appropriate size
        current_order = order
        while current_order <= self.max_order and not self.free_lists[current_order]:
            current_order += 1
        
        if current_order > self.max_order:
            print(f"No memory available for {size}KB request")
            return None
        
        # Take block from free list
        block = self.free_lists[current_order].pop(0)
        
        # Split if necessary
        while current_order > order:
            current_order -= 1
            buddy = block ^ (1 << current_order)
            self.free_lists[current_order].append(buddy)
        
        self.allocated_blocks[block] = {'size': 1 << order, 'order': order}
        print(f"Allocated {1 << order}KB at address {block:08b}")
        return block
    
    def free(self, block: int):
        """Free an allocated block"""
        if block not in self.allocated_blocks:
            print(f"Block at {block:08b} not allocated")
            return
        
        info = self.allocated_blocks[block]
        order = info['order']
        
        print(f"Freeing {info['size']}KB at address {block:08b}")
        
        # Try to coalesce with buddy
        while order < self.max_order:
            buddy = block ^ (1 << order)
            
            if buddy in self.free_lists[order]:
                # Remove buddy and coalesce
                self.free_lists[order].remove(buddy)
                block = min(block, buddy)
                order += 1
            else:
                break
        
        # Add to free list
        self.free_lists[order].append(block)
        self.free_lists[order].sort()
        del self.allocated_blocks[block]
    
    def print_state(self):
        """Print current state of the buddy system"""
        print("\nBuddy System State:")
        print("-" * 40)
        for order in range(self.max_order + 1):
            size = 1 << order
            if self.free_lists[order]:
                blocks = [f"{addr:08b}" for addr in self.free_lists[order]]
                print(f"Order {order} ({size}KB): {blocks}")
        
        print("\nAllocated Blocks:")
        for addr, info in self.allocated_blocks.items():
            print(f"  Address {addr:08b}: {info['size']}KB")

class SlabAllocator:
    """Implements Slab Allocation for kernel objects"""
    
    def __init__(self):
        self.caches = {}
        self.slab_states = {'full': [], 'empty': [], 'partial': []}
    
    def create_cache(self, name: str, object_size: int, num_objects: int = 10):
        """Create a cache for a specific kernel object type"""
        print(f"\nCreating cache '{name}' for objects of size {object_size} bytes")
        
        # Create initial slab
        slab = {
            'name': name,
            'object_size': object_size,
            'objects': [{'free': True, 'data': None} for _ in range(num_objects)],
            'free_count': num_objects
        }
        
        self.caches[name] = slab
        self.slab_states['empty'].append(slab)
        print(f"  Created slab with {num_objects} objects")
    
    def allocate_object(self, cache_name: str, data: str):
        """Allocate an object from a cache"""
        if cache_name not in self.caches:
            print(f"Cache '{cache_name}' not found")
            return None
        
        cache = self.caches[cache_name]
        
        # Try partial slabs first
        for slab in self.slab_states['partial'][:]:
            for i, obj in enumerate(slab['objects']):
                if obj['free']:
                    obj['free'] = False
                    obj['data'] = data
                    slab['free_count'] -= 1
                    
                    # Update slab state
                    self.update_slab_state(slab)
                    
                    print(f"Allocated object from partial slab, data='{data}'")
                    print(f"  Slab free count: {slab['free_count']}/{len(slab['objects'])}")
                    return (slab, i)
        
        # Try empty slabs
        if self.slab_states['empty']:
            slab = self.slab_states['empty'].pop(0)
            slab['objects'][0]['free'] = False
            slab['objects'][0]['data'] = data
            slab['free_count'] -= 1
            
            self.update_slab_state(slab)
            
            print(f"Allocated object from empty slab, data='{data}'")
            return (slab, 0)
        
        # Create new slab
        print("No free slabs, creating new slab")
        self.create_cache(cache_name, cache['object_size'])
        return self.allocate_object(cache_name, data)
    
    def free_object(self, slab, index: int):
        """Free an object"""
        slab['objects'][index]['free'] = True
        slab['objects'][index]['data'] = None
        slab['free_count'] += 1
        
        self.update_slab_state(slab)
        print(f"Freed object at index {index}")
        print(f"  Slab free count: {slab['free_count']}/{len(slab['objects'])}")
    
    def update_slab_state(self, slab):
        """Update slab's state based on free count"""
        # Remove from current state lists
        for state in self.slab_states.values():
            if slab in state:
                state.remove(slab)
                break
        
        # Add to appropriate state
        if slab['free_count'] == 0:
            self.slab_states['full'].append(slab)
        elif slab['free_count'] == len(slab['objects']):
            self.slab_states['empty'].append(slab)
        else:
            self.slab_states['partial'].append(slab)
    
    def print_state(self):
        """Print current state of slab allocator"""
        print("\nSlab Allocator State:")
        print("-" * 40)
        
        for state_name, slabs in self.slab_states.items():
            print(f"\n{state_name.upper()} slabs:")
            for slab in slabs:
                print(f"  {slab['name']}: {slab['free_count']}/{len(slab['objects'])} free")

def demonstrate_program_structure():
    """Demonstrates how program structure affects page faults"""
    print(f"\n{'='*60}")
    print("PROGRAM STRUCTURE AND PAGE FAULTS")
    print(f"{'='*60}")
    
    # Simulate 128x128 array where each row is on a different page
    print("\nProgram 1: Column-wise access (poor locality)")
    print("for j in range(128):")
    print("    for i in range(128):")
    print("        data[i][j] = 0")
    
    # Each access to a new column likely causes page fault
    page_faults_prog1 = 128 * 128  # Worst case: every element on different page
    print(f"Estimated page faults: {page_faults_prog1:,}")
    
    print("\nProgram 2: Row-wise access (good locality)")
    print("for i in range(128):")
    print("    for j in range(128):")
    print("        data[i][j] = 0")
    
    # Accessing rows sequentially has good locality
    page_faults_prog2 = 128  # One page fault per row
    print(f"Estimated page faults: {page_faults_prog2:,}")
    
    improvement = page_faults_prog1 / page_faults_prog2
    print(f"\nImprovement: {improvement:.1f}x fewer page faults!")

def plot_page_faults_vs_frames():
    """Creates a plot showing page faults vs number of frames"""
    print(f"\n{'='*60}")
    print("PAGE FAULTS vs FRAMES (Belady's Anomaly Demo)")
    print(f"{'='*60}")
    
    # Reference string from lecture
    ref_string = [7,0,1,2,0,3,0,4,2,3,0,3,0,3,2,1,2,0,1,7,0,1]
    
    frame_counts = list(range(1, 8))
    fifo_faults = []
    lru_faults = []
    opt_faults = []
    
    print("\nRunning simulations for different frame counts...")
    for frames in frame_counts:
        # FIFO
        fifo = DemandPagingSimulator(frames, DemandPagingSimulator.ReplacementAlgorithm.FIFO)
        for page in ref_string:
            fifo.access_page(page)
        fifo_faults.append(fifo.page_faults)
        
        # LRU
        lru = DemandPagingSimulator(frames, DemandPagingSimulator.ReplacementAlgorithm.LRU)
        for page in ref_string:
            lru.access_page(page)
        lru_faults.append(lru.page_faults)
        
        # Optimal (approximated)
        opt = DemandPagingSimulator(frames, DemandPagingSimulator.ReplacementAlgorithm.OPTIMAL)
        opt.access_history = ref_string.copy()
        for page in ref_string:
            opt.access_page(page)
        opt_faults.append(opt.page_faults)
        
        print(f"Frames={frames}: FIFO={fifo_faults[-1]}, LRU={lru_faults[-1]}, OPT={opt_faults[-1]}")
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(frame_counts, fifo_faults, 'bo-', label='FIFO', linewidth=2)
    plt.plot(frame_counts, lru_faults, 'ro-', label='LRU', linewidth=2)
    plt.plot(frame_counts, opt_faults, 'go-', label='Optimal', linewidth=2)
    
    plt.xlabel('Number of Frames', fontsize=12)
    plt.ylabel('Page Faults', fontsize=12)
    plt.title('Page Faults vs Number of Frames', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks(frame_counts)
    
    # Highlight Belady's Anomaly (FIFO sometimes worse with more frames)
    for i in range(1, len(frame_counts)):
        if fifo_faults[i] > fifo_faults[i-1]:
            plt.annotate('Belady\'s Anomaly!', 
                        xy=(frame_counts[i], fifo_faults[i]),
                        xytext=(frame_counts[i]+0.2, fifo_faults[i]+0.5),
                        arrowprops=dict(facecolor='red', shrink=0.05),
                        fontsize=10, color='red')
    
    plt.tight_layout()
    plt.savefig('page_faults_vs_frames.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    print("\nNote: Belady's Anomaly occurs when adding more frames")
    print("      INCREASES page faults (counter-intuitive!)")

def calculate_eat_example():
    """Calculates Effective Access Time example from lecture"""
    print(f"\n{'='*60}")
    print("EFFECTIVE ACCESS TIME CALCULATION")
    print(f"{'='*60}")
    
    memory_access_time = 200  # nanoseconds
    page_fault_service_time = 8_000_000  # nanoseconds (8ms)
    
    print(f"Memory access time: {memory_access_time} ns")
    print(f"Page fault service time: {page_fault_service_time:,} ns (8ms)")
    
    # Example from lecture: 1 fault per 1000 accesses
    p = 1 / 1000
    eat = (1 - p) * memory_access_time + p * page_fault_service_time
    
    print(f"\nWith page fault rate p = {p:.4f} (1 per 1000 accesses):")
    print(f"EAT = (1 - {p:.4f}) × {memory_access_time} + {p:.4f} × {page_fault_service_time:,}")
    print(f"    = {eat:,.2f} ns")
    print(f"    = {eat / 1000:,.2f} μs")
    print(f"Slowdown: {eat / memory_access_time:.1f}x")
    
    # Calculate maximum p for < 10% degradation
    max_eat = memory_access_time * 1.10  # 10% more
    max_p = (max_eat - memory_access_time) / (page_fault_service_time - memory_access_time)
    
    print(f"\nFor < 10% performance degradation:")
    print(f"Maximum acceptable page fault rate: p < {max_p:.8f}")
    print(f"Or less than 1 page fault every {int(1/max_p):,} memory accesses")

def demonstrate_numa_concept():
    """Demonstrates NUMA (Non-Uniform Memory Access) concept"""
    print(f"\n{'='*60}")
    print("NUMA (Non-Uniform Memory Access)")
    print(f"{'='*60}")
    
    print("\nIn NUMA systems, memory access time depends on location:")
    print("CPU0 ──┐")
    print("       ├─ Memory Bank 0 (Local: 100ns)")
    print("CPU1 ──┘")
    print("       ┌─ Memory Bank 1 (Remote: 300ns)")
    print("CPU2 ─┼─ Memory Bank 2 (Remote: 300ns)")
    print("CPU3 ─┘")
    
    print("\nSolaris solution: Igroups (latency groups)")
    print("• Schedule threads on same board as their memory")
    print("• Allocate memory 'close to' the CPU")
    print("• Reduces cross-board memory access latency")

def main():
    """Main function to run all demonstrations"""
    print("VIRTUAL MEMORY CONCEPTS DEMONSTRATION")
    print("=" * 60)
    
    # Example reference string from lecture
    reference_string = [7,0,1,2,0,3,0,4,2,3,0,3,0,3,2,1,2,0,1,7,0,1]
    
    # 1. Demonstrate different page replacement algorithms
    print("\n1. DEMAND PAGING WITH DIFFERENT ALGORITHMS")
    
    algorithms = [
        DemandPagingSimulator.ReplacementAlgorithm.FIFO,
        DemandPagingSimulator.ReplacementAlgorithm.LRU,
        DemandPagingSimulator.ReplacementAlgorithm.OPTIMAL,
        DemandPagingSimulator.ReplacementAlgorithm.CLOCK,
    ]
    
    for algo in algorithms:
        simulator = DemandPagingSimulator(3, algo)
        simulator.run_simulation(reference_string[:10])  # First 10 references
    
    # 2. Copy-on-Write demonstration
    print("\n\n2. COPY-ON-WRITE (COW) DEMONSTRATION")
    cow = CopyOnWriteSimulator()
    
    # Initialize parent process with some pages
    cow.shared_pages = {
        0: {'data': 'ParentData0', 'ref_count': 1},
        1: {'data': 'ParentData1', 'ref_count': 1},
        2: {'data': 'ParentData2', 'ref_count': 1}
    }
    cow.process_pages[1] = {
        0: {'data_ptr': 0},
        1: {'data_ptr': 1},
        2: {'data_ptr': 2}
    }
    
    cow.fork_process(1, 2)  # Fork process 2 from process 1
    cow.write_to_page(2, 1, "ChildModifiedData")  # Child modifies a page
    
    # 3. Working Set and Thrashing
    print("\n\n3. WORKING SET MODEL AND THRASHING")
    ws_simulator = WorkingSetSimulator(total_frames=50)
    ws_simulator.run_simulation(steps=15)
    
    # 4. Buddy System
    print("\n\n4. BUDDY SYSTEM ALLOCATION")
    buddy = BuddySystemAllocator(total_memory=256)  # 256KB
    buddy.print_state()
    
    # Allocate some blocks
    print("\nAllocating memory blocks:")
    block1 = buddy.allocate(21)  # 21KB -> rounds to 32KB
    block2 = buddy.allocate(64)  # 64KB
    block3 = buddy.allocate(16)  # 16KB
    
    buddy.print_state()
    
    # Free a block
    print("\nFreeing a block:")
    if block2:
        buddy.free(block2)
    buddy.print_state()
    
    # 5. Slab Allocation
    print("\n\n5. SLAB ALLOCATION")
    slab = SlabAllocator()
    
    # Create caches for different kernel objects
    slab.create_cache("task_struct", 1700)  # Process descriptor
    slab.create_cache("inode", 512)        # File inode
    slab.create_cache("dentry", 192)       # Directory entry
    
    slab.print_state()
    
    # Allocate some objects
    print("\nAllocating objects:")
    obj1 = slab.allocate_object("task_struct", "Process A")
    obj2 = slab.allocate_object("task_struct", "Process B")
    obj3 = slab.allocate_object("inode", "File X")
    
    slab.print_state()
    
    # Free an object
    print("\nFreeing an object:")
    if obj1:
        slab.free_object(*obj1)
    slab.print_state()
    
    # 6. Program structure impact
    demonstrate_program_structure()
    
    # 7. EAT calculation
    calculate_eat_example()
    
    # 8. NUMA concept
    demonstrate_numa_concept()
    
    # 9. Page faults vs frames plot (with Belady's Anomaly)
    try:
        plot_page_faults_vs_frames()
    except ImportError:
        print("\nNote: Matplotlib not installed. Skipping plot generation.")
        print("Install with: pip install matplotlib")
    
    print(f"\n{'='*60}")
    print("ALL DEMONSTRATIONS COMPLETE!")
    print(f"{'='*60}")
    print("\nKey concepts demonstrated:")
    print("1. Demand Paging & Page Fault Handling")
    print("2. Page Replacement Algorithms (FIFO, LRU, Optimal, Clock)")
    print("3. Copy-on-Write efficiency")
    print("4. Working Set Model & Thrashing detection")
    print("5. Buddy System for kernel memory")
    print("6. Slab Allocation for kernel objects")
    print("7. Program structure impact on locality")
    print("8. Effective Access Time calculation")
    print("9. NUMA architecture considerations")
    print("10. Belady's Anomaly visualization")

if __name__ == "__main__":
    main()
