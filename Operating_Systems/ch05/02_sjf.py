def sjf_scheduling(processes):
    """
    SJF Scheduling Algorithm (Non-preemptive)
    """
    processes = sorted(processes, key=lambda x: x[1])  # Sort by arrival time
    current_time = 0
    completed = 0
    n = len(processes)
    results = []
    visited = [False] * n
    
    while completed != n:
        # Find available processes at current time
        available = []
        for i in range(n):
            if not visited[i] and processes[i][1] <= current_time:
                available.append((i, processes[i][2]))  # (index, burst_time)
        
        if not available:
            current_time += 1
            continue
        
        # Select process with shortest burst time
        available.sort(key=lambda x: x[1])
        idx, burst = available[0]
        pid, arrival, burst = processes[idx]
        
        # Calculate metrics
        completion = current_time + burst
        turnaround = completion - arrival
        waiting = turnaround - burst
        
        results.append({
            'pid': pid,
            'arrival': arrival,
            'burst': burst,
            'completion': completion,
            'turnaround': turnaround,
            'waiting': waiting
        })
        
        current_time = completion
        visited[idx] = True
        completed += 1
    
    return results

# Example usage
processes_sjf = [
    ('P1', 0, 6),
    ('P2', 0, 8),
    ('P3', 0, 7),
    ('P4', 0, 3)
]
# Example usage
processes_sjf = [
    ('P1', 0, 6),
    ('P2', 0, 2),
    ('P3', 0, 7),
    ('P4', 0, 3)
]


print("\nSJF Scheduling:")
print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8}")
for p in sjf_scheduling(processes_sjf):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8}") 
