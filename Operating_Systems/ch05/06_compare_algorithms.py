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



def compare_algorithms(processes, quantum=4):
    """
    Compare all scheduling algorithms
    """
    print("=" * 80)
    print("SCHEDULING ALGORITHM COMPARISON")
    print("=" * 80)
    
    algorithms = [
        ("FCFS", fcfs_scheduling),
        ("SJF", sjf_scheduling),
        ("SRTF", srtf_scheduling),
        ("Priority", priority_scheduling)
    ]
    
    comparison_results = {}
    
    for name, algorithm in algorithms:
        if name == "Priority":
            # Need priority values for priority scheduling
            # Let's assign random priorities for demonstration
            import random
            processes_with_priority = [(p[0], p[1], p[2], random.randint(1, 5)) for p in processes]
            results = algorithm(processes_with_priority)
        elif name == "SRTF" or name == "SJF":
            results = algorithm(processes)
        else:
            results = algorithm(processes)
        
        # Calculate averages
        avg_waiting = sum(p['waiting'] for p in results) / len(results)
        avg_turnaround = sum(p['turnaround'] for p in results) / len(results)
        
        comparison_results[name] = {
            'avg_waiting': avg_waiting,
            'avg_turnaround': avg_turnaround,
            'throughput': len(processes) / max(p['completion'] for p in results)
        }
    
    # RR needs separate handling
    results_rr = round_robin_scheduling(processes, quantum)
    avg_waiting_rr = sum(p['waiting'] for p in results_rr) / len(results_rr)
    avg_turnaround_rr = sum(p['turnaround'] for p in results_rr) / len(results_rr)
    
    comparison_results['RR'] = {
        'avg_waiting': avg_waiting_rr,
        'avg_turnaround': avg_turnaround_rr,
        'throughput': len(processes) / max(p['completion'] for p in results_rr)
    }
    
    # Display comparison
    print(f"\n{'Algorithm':<12} {'Avg Waiting':<15} {'Avg Turnaround':<15} {'Throughput':<15}")
    print("-" * 57)
    
    for algo in ['FCFS', 'SJF', 'SRTF', 'RR', 'Priority']:
        data = comparison_results[algo]
        print(f"{algo:<12} {data['avg_waiting']:<15.2f} {data['avg_turnaround']:<15.2f} {data['throughput']:<15.4f}")
    
    return comparison_results

# Run comparison
test_processes = [
    ('P1', 0, 6),
    ('P2', 1, 8),
    ('P3', 2, 7),
    ('P4', 3, 3)
]

compare_algorithms(test_processes) 
