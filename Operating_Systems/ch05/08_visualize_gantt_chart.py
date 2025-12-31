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




def visualize_gantt_chart(processes, schedule_result):
    """
    Create a simple text-based Gantt chart
    """
    print("\nGANTT CHART:")
    print("-" * 60)
    
    timeline = []
    for p in schedule_result:
        pid = p['pid']
        start = p['completion'] - p['burst']
        end = p['completion']
        timeline.append((pid, start, end))
    
    # Sort by start time
    timeline.sort(key=lambda x: x[1])
    
    # Print timeline
    current_time = 0
    for pid, start, end in timeline:
        if start > current_time:
            print(f"| IDLE({current_time}-{start}) ", end="")
        print(f"| {pid}({start}-{end}) ", end="")
        current_time = end
    
    print("|")
    print("-" * 60)

# Example visualization
# Example usage
processes_fcfs = [
    ('P1', 0, 24),
    ('P2', 1, 3),
    ('P3', 2, 3)
]

print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8}")
for p in fcfs_scheduling(processes_fcfs):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8}") 
    
print("\nVisualizing FCFS Gantt Chart:")
results_fcfs = fcfs_scheduling(processes_fcfs)
visualize_gantt_chart(processes_fcfs, results_fcfs) 

# Example usage
processes_sjf = [
    ('P1', 0, 6),
    ('P2', 0, 8),
    ('P3', 0, 7),
    ('P4', 0, 3)
]

print("\nSJF Scheduling:")
print(f"{'PID':<5} {'Arrival':<8} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8}")
for p in sjf_scheduling(processes_sjf):
    print(f"{p['pid']:<5} {p['arrival']:<8} {p['burst']:<6} {p['completion']:<10} {p['turnaround']:<10} {p['waiting']:<8}") 


print("\nVisualizing SJF Gantt Chart:")
results_sjf = sjf_scheduling(processes_sjf)
visualize_gantt_chart(processes_sjf, results_sjf) 

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
    
print("\nVisualizing SRTF Gantt Chart:")
results_srtf = srtf_scheduling(processes_srtf)
visualize_gantt_chart(processes_srtf, results_srtf) 

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

print("\nVisualizing Round Robin Gantt Chart:")
results_rr = round_robin_scheduling(processes_rr, 4)
visualize_gantt_chart(processes_rr, results_rr) 


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

print("\nVisualizing Priority Gantt Chart:")
results_priority = priority_scheduling(processes_priority)
visualize_gantt_chart(processes_priority, results_priority) 
