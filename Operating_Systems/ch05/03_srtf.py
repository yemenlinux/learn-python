def srtf_scheduling(processes):
    """
    SRTF Scheduling Algorithm (Preemptive)
    """
    n = len(processes)
    remaining_time = [p[2] for p in processes]
    arrival_time = [p[1] for p in processes]
    
    current_time = 0
    completed = 0
    prev = -1
    completion_time = [0] * n
    response_time = [-1] * n
    
    while completed != n:
        # Find process with minimum remaining time among arrived processes
        min_remaining = float('inf')
        idx = -1
        
        for i in range(n):
            if arrival_time[i] <= current_time and remaining_time[i] > 0:
                if remaining_time[i] < min_remaining:
                    min_remaining = remaining_time[i]
                    idx = i
        
        if idx == -1:
            current_time += 1
            continue
        
        # Record response time if this is first time process gets CPU
        if response_time[idx] == -1:
            response_time[idx] = current_time - arrival_time[idx]
        
        # Execute for 1 time unit (preemptive)
        remaining_time[idx] -= 1
        current_time += 1
        
        # If process completed
        if remaining_time[idx] == 0:
            completed += 1
            completion_time[idx] = current_time
            prev = idx
    
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
processes_srtf = [
    ('P1', 0, 8),
    ('P2', 1, 4),
    ('P3', 2, 9),
    ('P4', 3, 5)
]

print("\nSRTF Scheduling:")
print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8} {'Response':<8}")
for p in srtf_scheduling(processes_srtf):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8} {p['response']:<8}") 
