# How to Use:

## Run the complete demonstration:
```python
python virtual_memory_simulator.py
```

## Run specific components:

```python
# Test just FIFO algorithm
fifo = DemandPagingSimulator(3, DemandPagingSimulator.ReplacementAlgorithm.FIFO)
fifo.run_simulation([7,0,1,2,0,3,0,4,2,3])

# Test COW
cow = CopyOnWriteSimulator()
# ... initialize and test

# Test Buddy System
buddy = BuddySystemAllocator(256)
buddy.allocate(21)
buddy.print_state()

```
