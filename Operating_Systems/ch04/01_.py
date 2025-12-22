"""
COMPREHENSIVE THREADS & CONCURRENCY CONCEPTS IN PYTHON
Corresponding to Lecture Chapter 4

This script demonstrates key threading and concurrency concepts
from the Operating System Concepts textbook using Python.
"""

import threading
import multiprocessing
import concurrent.futures
import time
import random
import queue
from threading import Thread, Lock, Condition, Semaphore, local as thread_local
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial

print("=" * 60)
print("THREADS & CONCURRENCY IN PYTHON")
print("=" * 60)

# ============================================================================
# SLIDES 1-4: INTRODUCTION & MOTIVATION
# ============================================================================
print("\n" + "="*60)
print("SLIDES 1-4: Introduction & Motivation for Threads")
print("="*60)

print("""
KEY CONCEPTS:
- Threads are lightweight processes within a program
- Multiple threads can run concurrently within same process
- Threads share memory space, making communication easier than processes
- Modern applications (web servers, GUI apps) heavily use threads
""")

def motivation_example():
    """Demonstrates why we need threads (like Slide 5's Word Processor example)"""
    print("\nExample: Multi-threaded Application (like Word Processor):")
    print("- Thread 1: Accept user input")
    print("- Thread 2: Auto-save document")
    print("- Thread 3: Check spelling in background")
    print("- Thread 4: Update UI display")
    print("\nAll these can happen concurrently!")

motivation_example() 
