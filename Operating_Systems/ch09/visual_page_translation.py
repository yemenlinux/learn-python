#!/usr/bin/env python3
"""
Visual Page Table Simulation
Shows step-by-step address translation for different page table structures
"""

import time

class VisualPageTranslation:
    """Visual demonstration of page translation"""
    
    @staticmethod
    def hierarchical_paging_visual():
        """Visualize hierarchical paging translation"""
        print("\n" + "="*60)
        print("VISUAL: Hierarchical Paging Address Translation")
        print("="*60)
        
        # 32-bit address: 0x12345678
        va = 0x12345678
        print(f"Virtual Address: 0x{va:08x}")
        print()
        
        # Step 1: Split address
        print("Step 1: Split address into components")
        print("32-bit address format for 2-level paging with 4KB pages:")
        print("  Bits 31-22: Outer page index (10 bits)")
        print("  Bits 21-12: Inner page index (10 bits)")
        print("  Bits 11-0:  Offset (12 bits)")
        print()
        
        # Calculate components
        outer = (va >> 22) & 0x3FF  # 10 bits
        inner = (va >> 12) & 0x3FF  # 10 bits
        offset = va & 0xFFF         # 12 bits
        
        print(f"  Outer index: {outer} (0x{outer:03x})")
        print(f"  Inner index: {inner} (0x{inner:03x})")
        print(f"  Offset:      {offset} (0x{offset:03x})")
        print()
        
        # Step 2: Outer page table lookup
        print("Step 2: Lookup in Outer Page Table")
        print(f"  Use outer index {outer} as index into outer page table")
        print(f"  Outer page table entry contains address of inner page table")
        print(f"  Let's say outer[{outer}] = 0x5000 (address of inner page table)")
        print()
        
        # Step 3: Inner page table lookup
        print("Step 3: Lookup in Inner Page Table")
        print(f"  Go to inner page table at 0x5000")
        print(f"  Use inner index {inner} as index into inner page table")
        print(f"  Inner page table entry contains frame number")
        print(f"  Let's say inner[{inner}] = frame 42")
        print()
        
        # Step 4: Calculate physical address
        print("Step 4: Calculate Physical Address")
        frame = 42
        pa = (frame << 12) | offset
        print(f"  Physical Address = (frame << 12) | offset")
        print(f"                   = (42 << 12) | 0x{offset:03x}")
        print(f"                   = 0x{frame << 12:08x} | 0x{offset:03x}")
        print(f"                   = 0x{pa:08x}")
        print()
        
        print(f"Translation: 0x{va:08x} (virtual) → 0x{pa:08x} (physical)")
        print("="*60)
    
    @staticmethod
    def hashed_page_table_visual():
        """Visualize hashed page table translation"""
        print("\n" + "="*60)
        print("VISUAL: Hashed Page Table Translation")
        print("="*60)
        
        pid = 123
        va = 0x000123456789ABCD  # 64-bit address
        page_size = 4096
        page_number = va // page_size
        offset = va % page_size
        
        print(f"Process ID: {pid}")
        print(f"Virtual Address: 0x{va:016x}")
        print(f"Page Size: {page_size} bytes (0x{page_size:04x})")
        print(f"Page Number: {page_number} (0x{page_number:012x})")
        print(f"Offset: {offset} (0x{offset:03x})")
        print()
        
        print("Step 1: Create hash key")
        print(f"  Key = hash(pid, page_number)")
        print(f"      = hash({pid}, 0x{page_number:012x})")
        print()
        
        print("Step 2: Compute hash value")
        print(f"  hash_value = hash_function(key) mod hash_table_size")
        print(f"  Let's say hash_value = 742")
        print()
        
        print("Step 3: Search hash bucket")
        print("  Hash table has chains for collision resolution")
        print("  Bucket 742 contains a linked list of entries")
        print("  Each entry contains: (pid, virtual_page, frame)")
        print("  We search the chain for matching (pid, virtual_page)")
        print()
        
        print("Step 4: Found entry")
        print(f"  Found entry: pid={pid}, virtual_page=0x{page_number:012x}, frame=8192")
        frame = 8192
        print()
        
        print("Step 5: Calculate physical address")
        pa = (frame * page_size) + offset
        print(f"  Physical Address = (frame * page_size) + offset")
        print(f"                   = (8192 * 4096) + 0x{offset:03x}")
        print(f"                   = 0x{frame * page_size:016x} + 0x{offset:03x}")
        print(f"                   = 0x{pa:016x}")
        print()
        
        print(f"Translation: 0x{va:016x} (virtual) → 0x{pa:016x} (physical)")
        print("="*60)
    
    @staticmethod
    def inverted_page_table_visual():
        """Visualize inverted page table translation"""
        print("\n" + "="*60)
        print("VISUAL: Inverted Page Table Translation")
        print("="*60)
        
        pid = 456
        va = 0xFFFF87654321
        page_size = 4096
        page_number = va // page_size
        offset = va % page_size
        
        print(f"Process ID: {pid}")
        print(f"Virtual Address: 0x{va:012x}")
        print(f"Page Number: {page_number} (0x{page_number:09x})")
        print(f"Offset: {offset} (0x{offset:03x})")
        print()
        
        print("Inverted Page Table Structure:")
        print("  - One entry per physical frame")
        print("  - Each entry contains: (pid, virtual_page)")
        print("  - Table is indexed by frame number")
        print()
        
        print("Step 1: Search for (pid, virtual_page) in table")
        print("  We need to find which frame contains our page")
        print("  Options:")
        print("    1. Linear search through all frames (slow)")
        print("    2. Use hash table for faster lookup")
        print()
        
        print("Step 2: Using hash table (common optimization)")
        print(f"  Lookup key = hash(pid, virtual_page)")
        print(f"  Hash table gives us frame number")
        print(f"  Let's say we get frame = 32768")
        frame = 32768
        print()
        
        print("Step 3: Verify entry in inverted table")
        print(f"  Check inverted_table[{frame}]")
        print(f"  Should contain: ({pid}, {page_number})")
        print("  If it matches, we found the right frame")
        print()
        
        print("Step 4: Calculate physical address")
        pa = (frame * page_size) + offset
        print(f"  Physical Address = (frame * page_size) + offset")
        print(f"                   = (32768 * 4096) + 0x{offset:03x}")
        print(f"                   = 0x{frame * page_size:012x} + 0x{offset:03x}")
        print(f"                   = 0x{pa:012x}")
        print()
        
        print("Key Insight:")
        print("  - Inverted table size = number of physical frames")
        print("  - Doesn't grow with virtual address space")
        print("  - Great for 64-bit systems with huge virtual spaces")
        print()
        
        print(f"Translation: 0x{va:012x} (virtual) → 0x{pa:012x} (physical)")
        print("="*60)

def main():
    """Run visual demonstrations"""
    print("VISUAL PAGE TRANSLATION DEMONSTRATIONS")
    print()
    
    vpt = VisualPageTranslation()
    
    while True:
        print("\nSelect visualization:")
        print("1. Hierarchical Paging (32-bit, 2-level)")
        print("2. Hashed Page Tables (64-bit)")
        print("3. Inverted Page Tables")
        print("4. All visualizations")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == "1":
            vpt.hierarchical_paging_visual()
        elif choice == "2":
            vpt.hashed_page_table_visual()
        elif choice == "3":
            vpt.inverted_page_table_visual()
        elif choice == "4":
            vpt.hierarchical_paging_visual()
            vpt.hashed_page_table_visual()
            vpt.inverted_page_table_visual()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
