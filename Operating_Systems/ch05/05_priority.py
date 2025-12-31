def priority_scheduling(processes):
    """
    Priority Scheduling Algorithm (Non-preemptive)
    Lower number = higher priority
    """
    processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time
    n = len(processes)
    current_time = 0
    completed = 0
    visited = [False] * n
    results = []
    
    while completed != n:
        # Find available processes
        available = []
        for i in range(n):
            if not visited[i] and processes[i][1] <= current_time:
                # (index, priority, burst_time)
                available.append((i, processes[i][3], processes[i][2]))
        
        if not available:
            current_time += 1
            continue
        
        # Select process with highest priority (lowest number)
        available.sort(key=lambda x: x[1])
        idx, priority, burst = available[0]
        pid, arrival, burst, priority = processes[idx]
        
        # Calculate metrics
        completion = current_time + burst
        turnaround = completion - arrival
        waiting = turnaround - burst
        
        results.append({
            'pid': pid,
            'arrival': arrival,
            'burst': burst,
            'priority': priority,
            'completion': completion,
            'turnaround': turnaround,
            'waiting': waiting
        })
        
        current_time = completion
        visited[idx] = True
        completed += 1
    
    return results

# Example usage
processes_priority = [
    ('P1', 0, 10, 3),
    ('P2', 0, 1, 1),
    ('P3', 0, 2, 4),
    ('P4', 0, 1, 5),
    ('P5', 0, 5, 2)
]

print("\nPriority Scheduling:")
print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Priority':<8} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8}")
for p in priority_scheduling(processes_priority):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['priority']:<8} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8}") 
