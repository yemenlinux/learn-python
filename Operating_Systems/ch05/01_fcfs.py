def fcfs_scheduling(processes):
    """
    FCFS Scheduling Algorithm
    
    processes: list of tuples (process_id, arrival_time, burst_time)
    returns: dict with completion, turnaround, waiting times
    """
    # Sort processes by arrival time
    processes = sorted(processes, key=lambda x: x[1])
    
    current_time = 0
    results = []
    
    for pid, arrival, burst in processes:
        # If process arrives after current time
        if arrival > current_time:
            current_time = arrival
        
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
    
    return results

# Example usage
processes_fcfs = [
    ('P1', 0, 24),
    ('P2', 1, 3),
    ('P3', 2, 3)
]

# Example usage
processes_fcfs = [
    ('P1', 0, 9),
    ('P2', 1, 5),
    ('P3', 2, 3)
]

print("FCFS Scheduling:")
print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8}")
for p in fcfs_scheduling(processes_fcfs):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8}") 
