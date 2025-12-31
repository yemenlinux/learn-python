def round_robin_scheduling(processes, quantum):
    """
    Round Robin Scheduling Algorithm
    """
    n = len(processes)
    remaining_time = [p[2] for p in processes]
    arrival_time = [p[1] for p in processes]
    
    current_time = 0
    completion_time = [0] * n
    response_time = [-1] * n
    
    # Create ready queue
    ready_queue = []
    completed = 0
    i = 0
    
    # Sort processes by arrival time
    sorted_indices = sorted(range(n), key=lambda i: arrival_time[i])
    idx = 0
    
    while completed < n:
        # Add processes that have arrived to ready queue
        while idx < n and arrival_time[sorted_indices[idx]] <= current_time:
            ready_queue.append(sorted_indices[idx])
            idx += 1
        
        if not ready_queue:
            current_time += 1
            continue
        
        # Get next process from ready queue
        process_idx = ready_queue.pop(0)
        
        # Record response time if first time
        if response_time[process_idx] == -1:
            response_time[process_idx] = current_time - arrival_time[process_idx]
        
        # Execute for quantum or remaining time (whichever is smaller)
        exec_time = min(quantum, remaining_time[process_idx])
        remaining_time[process_idx] -= exec_time
        current_time += exec_time
        
        # Add newly arrived processes during execution
        while idx < n and arrival_time[sorted_indices[idx]] <= current_time:
            ready_queue.append(sorted_indices[idx])
            idx += 1
        
        # If process not finished, add back to queue
        if remaining_time[process_idx] > 0:
            ready_queue.append(process_idx)
        else:
            completed += 1
            completion_time[process_idx] = current_time
    
    # Calculate metrics
    results = []
    for i in range(n):
        pid = processes[i][0]
        arrival = arrival_time[i]
        burst = processes[i][2]
        completion = completion_time[i]
        turnaround = completion - arrival
        waiting = turnaround - burst
        
        results.append({
            'pid': pid,
            'arrival': arrival,
            'burst': burst,
            'completion': completion,
            'turnaround': turnaround,
            'waiting': waiting,
            'response': response_time[i]
        })
    
    return results

# Example usage
processes_rr = [
    ('P1', 0, 24),
    ('P2', 0, 3),
    ('P3', 0, 3)
]

print("\nRound Robin Scheduling (Quantum = 4):")
print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8} {'Response':<8}")
for p in round_robin_scheduling(processes_rr, 4):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8} {p['response']:<8}") 
