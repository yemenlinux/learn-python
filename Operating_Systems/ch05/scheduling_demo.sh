#!/bin/bash

# ============================================================================
# CPU Scheduling Algorithms Demonstrator
# A comprehensive bash script demonstrating various scheduling concepts
# ============================================================================

clear
echo "=================================================================="
echo "          CPU SCHEDULING ALGORITHMS DEMONSTRATOR"
echo "=================================================================="
echo ""

# Colors for better visualization
RED='\e[0;31m'
GREEN='\e[0;32m'
YELLOW='\e[0;33m'
BLUE='\e[0;34m'
PURPLE='\033[0;35m'
CYAN='\e[0;36m'
NC='\e[0m' # No Color
BOLD='\e[1m'
UNDERLINE='\e[4m'

# Function to print section headers
section() {
    echo -e "\n${CYAN}${BOLD}=================================================================="
    echo -e "  $1"
    echo -e "==================================================================${NC}\n"
}

# Function to print step-by-step explanations
explain() {
    echo -e "${YELLOW}[EXPLAIN]${NC} $1"
}

# Function to display Gantt chart
show_gantt() {
    echo -e "\n${GREEN}GANTT CHART:${NC}"
    echo -e "${BLUE}┌──────────────────────────────────────────────────────────┐${NC}"
    printf "${BLUE}│${NC}"
    local time=0
    for ((i=0; i<${#gantt_pid[@]}; i++)); do
        local pid=${gantt_pid[$i]}
        local start=${gantt_start[$i]}
        local end=${gantt_end[$i]}
        
        if [ $time -lt $start ]; then
            local idle_time=$((start - time))
            printf " ${RED}IDLE($time-$start)${NC} │"
            time=$start
        fi
        
        printf " ${GREEN}P$pid($start-$end)${NC} │"
        time=$end
    done
    echo -e "\n${BLUE}└──────────────────────────────────────────────────────────┘${NC}"
}

# ============================================================================
# 1. BASIC CONCEPTS - CPU BURST CYCLE
# ============================================================================
section "1. BASIC CONCEPTS - CPU BURST CYCLE"

echo -e "${BOLD}CPU-I/O Burst Cycle Pattern:${NC}"
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo "│ Process Execution Lifecycle:                               │"
echo "│                                                            │"
echo "│   ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐     │"
echo "│   │ CPU │    │ I/O │    │ CPU │    │ I/O │    │ CPU │ ... │"
echo "│   │burst│    │wait │    │burst│    │wait │    │burst│     │"
echo "│   └─────┘    └─────┘    └─────┘    └─────┘    └─────┘     │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""
explain "Processes alternate between CPU execution (burst) and I/O waiting"
explain "Scheduler's job: maximize CPU utilization during I/O waits"
read -p "Press Enter to continue..."

# ============================================================================
# 2. FCFS SCHEDULING
# ============================================================================
section "2. FIRST-COME FIRST-SERVED (FCFS) SCHEDULING"

# Define processes for FCFS: (PID, Arrival Time, Burst Time)
declare -A processes_fcfs=(
    ["P1"]="0 24"
    ["P2"]="1 3"
    ["P3"]="2 3"
)

echo -e "${BOLD}Process List:${NC}"
echo "┌──────┬──────────────┬────────────┐"
echo "│ PID  │ Arrival Time │ Burst Time │"
echo "├──────┼──────────────┼────────────┤"
for pid in "${!processes_fcfs[@]}"; do
    read arrival burst <<< "${processes_fcfs[$pid]}"
    printf "│ %-4s │ %-12s │ %-10s │\n" "$pid" "$arrival" "$burst"
done
echo "└──────┴──────────────┴────────────┘"
echo ""

# Simulate FCFS
echo -e "${BOLD}FCFS Execution Timeline:${NC}"

# Initialize Gantt chart arrays
declare -a gantt_pid=()
declare -a gantt_start=()
declare -a gantt_end=()
declare -A completion_time=()
declare -A turnaround_time=()
declare -A waiting_time=()

current_time=0
for pid in "P1" "P2" "P3"; do
    read arrival burst <<< "${processes_fcfs[$pid]}"
    
    if [ $arrival -gt $current_time ]; then
        # Add idle time to Gantt chart
        gantt_pid+=("IDLE")
        gantt_start+=($current_time)
        gantt_end+=($arrival)
        current_time=$arrival
    fi
    
    # Add process execution to Gantt chart
    gantt_pid+=("${pid:1}")
    gantt_start+=($current_time)
    gantt_end+=($((current_time + burst)))
    
    # Calculate metrics
    completion_time[$pid]=$((current_time + burst))
    turnaround_time[$pid]=$((completion_time[$pid] - arrival))
    waiting_time[$pid]=$((turnaround_time[$pid] - burst))
    
    current_time=$((current_time + burst))
done

show_gantt

echo -e "\n${BOLD}Performance Metrics:${NC}"
echo "┌──────┬──────────────┬────────────┬────────────────┬────────────────┬────────────┐"
echo "│ PID  │ Arrival Time │ Burst Time │ Completion Time│ Turnaround Time│ Waiting Time│"
echo "├──────┼──────────────┼────────────┼────────────────┼────────────────┼────────────┤"
total_wait=0
total_turnaround=0
for pid in "P1" "P2" "P3"; do
    read arrival burst <<< "${processes_fcfs[$pid]}"
    printf "│ %-4s │ %-12s │ %-10s │ %-14s │ %-14s │ %-10s │\n" \
        "$pid" "$arrival" "$burst" \
        "${completion_time[$pid]}" "${turnaround_time[$pid]}" "${waiting_time[$pid]}"
    total_wait=$((total_wait + ${waiting_time[$pid]}))
    total_turnaround=$((total_turnaround + ${turnaround_time[$pid]}))
done
echo "└──────┴──────────────┴────────────┴────────────────┴────────────────┴────────────┘"

avg_wait=$(echo "scale=2; $total_wait / 3" | bc)
avg_turnaround=$(echo "scale=2; $total_turnaround / 3" | bc)
echo -e "\n${BOLD}Average Waiting Time:${NC} $avg_wait ms"
echo -e "${BOLD}Average Turnaround Time:${NC} $avg_turnaround ms"
echo -e "\n${RED}⚠ CONVOY EFFECT:${NC} Short process P2 waits behind long process P1 (24ms!)"

read -p "Press Enter to continue..."

# ============================================================================
# 3. SJF SCHEDULING
# ============================================================================
section "3. SHORTEST JOB FIRST (SJF) SCHEDULING"

# Define processes for SJF: (PID, Arrival Time, Burst Time)
declare -A processes_sjf=(
    ["P1"]="0 6"
    ["P2"]="0 8"
    ["P3"]="0 7"
    ["P4"]="0 3"
)

echo -e "${BOLD}Process List (all arrive at time 0):${NC}"
echo "┌──────┬──────────────┬────────────┐"
echo "│ PID  │ Arrival Time │ Burst Time │"
echo "├──────┼──────────────┼────────────┤"
for pid in "${!processes_sjf[@]}"; do
    read arrival burst <<< "${processes_sjf[$pid]}"
    printf "│ %-4s │ %-12s │ %-10s │\n" "$pid" "$arrival" "$burst"
done
echo "└──────┴──────────────┴────────────┘"
echo ""

explain "SJF selects the process with the shortest burst time first"
explain "This minimizes average waiting time (mathematically proven optimal)"

# Sort by burst time (SJF)
echo -e "\n${BOLD}SJF Execution Order (by burst time):${NC}"
{
    for pid in "${!processes_sjf[@]}"; do
        read arrival burst <<< "${processes_sjf[$pid]}"
        echo "$burst $pid"
    done
} | sort -n | while read burst pid; do
    echo "  $pid (burst: $burst ms)"
done

# Simulate SJF
current_time=0
total_wait=0
total_turnaround=0
process_count=0

echo -e "\n${BOLD}SJF Execution Timeline:${NC}"

{
    for pid in "${!processes_sjf[@]}"; do
        read arrival burst <<< "${processes_sjf[$pid]}"
        echo "$burst $pid $arrival"
    done
} | sort -n | while read burst pid arrival; do
    waiting=$((current_time - arrival))
    if [ $waiting -lt 0 ]; then
        waiting=0
    fi
    completion=$((current_time + burst))
    turnaround=$((completion - arrival))
    
    echo "  Time $current_time: Start $pid (wait: ${waiting}ms)"
    echo "  Time $completion: Finish $pid (turnaround: ${turnaround}ms)"
    
    total_wait=$((total_wait + waiting))
    total_turnaround=$((total_turnaround + turnaround))
    current_time=$completion
    process_count=$((process_count + 1))
done

avg_wait=$(echo "scale=2; $total_wait / $process_count" | bc)
avg_turnaround=$(echo "scale=2; $total_turnaround / $process_count" | bc)
echo -e "\n${GREEN}✓ Average Waiting Time:${NC} $avg_wait ms"
echo -e "${GREEN}✓ Average Turnaround Time:${NC} $avg_turnaround ms"

echo -e "\n${YELLOW}[ISSUE]${NC} How do we know the burst time in advance?"
echo "  → Use exponential averaging for prediction"
echo "  → Formula: τₙ₊₁ = α × tₙ + (1-α) × τₙ"
echo "  where: tₙ = actual burst, τₙ = predicted burst, α = weight (0≤α≤1)"

read -p "Press Enter to continue..."

# ============================================================================
# 4. ROUND ROBIN SCHEDULING
# ============================================================================
section "4. ROUND ROBIN (RR) SCHEDULING"

echo -e "${BOLD}Round Robin Algorithm:${NC}"
echo "┌────────────────────────────────────────────────────────────┐"
echo "│ Each process gets a fixed time slice (quantum)             │"
echo "│ If not finished, goes to back of ready queue               │"
echo "│ Timer interrupt triggers context switch at quantum end     │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

# Define processes for RR: (PID, Arrival Time, Burst Time)
declare -A processes_rr=(
    ["P1"]="0 24"
    ["P2"]="0 3"
    ["P3"]="0 3"
)

quantum=4
echo -e "${BOLD}Process List (Quantum = $quantum ms):${NC}"
echo "┌──────┬──────────────┬────────────┐"
echo "│ PID  │ Arrival Time │ Burst Time │"
echo "├──────┼──────────────┼────────────┤"
for pid in "${!processes_rr[@]}"; do
    read arrival burst <<< "${processes_rr[$pid]}"
    printf "│ %-4s │ %-12s │ %-10s │\n" "$pid" "$arrival" "$burst"
done
echo "└──────┴──────────────┴────────────┘"

echo -e "\n${BOLD}Round Robin Simulation:${NC}"
echo "Time | Event"
echo "─────┼────────────────────────────────────"

# Initialize remaining burst times
declare -A remaining=()
for pid in "${!processes_rr[@]}"; do
    read arrival burst <<< "${processes_rr[$pid]}"
    remaining[$pid]=$burst
done

# Queue simulation
queue=("P1" "P2" "P3")
current_time=0
completed=0

while [ $completed -lt ${#processes_rr[@]} ]; do
    pid=${queue[0]}
    queue=("${queue[@]:1}")  # Remove first element
    
    if [ -z "$pid" ]; then
        break
    fi
    
    read arrival burst <<< "${processes_rr[$pid]}"
    remaining_burst=${remaining[$pid]}
    
    if [ $remaining_burst -gt 0 ]; then
        # Execute for quantum or remaining time
        execute_time=$((remaining_burst < quantum ? remaining_burst : quantum))
        echo "$(printf "%4d" $current_time) | Start $pid for ${execute_time}ms"
        
        remaining[$pid]=$((remaining_burst - execute_time))
        current_time=$((current_time + execute_time))
        
        if [ ${remaining[$pid]} -eq 0 ]; then
            echo "$(printf "%4d" $current_time) | $pid COMPLETED"
            completed=$((completed + 1))
        else
            # Add back to queue if not finished
            queue+=("$pid")
            echo "$(printf "%4d" $current_time) | $pid preempted, remaining: ${remaining[$pid]}ms"
        fi
    fi
done

echo -e "\n${BOLD}RR Characteristics:${NC}"
echo "  • Fair: Every process gets CPU time"
echo "  • Good response time for interactive processes"
echo "  • Quantum too large → behaves like FCFS"
echo "  • Quantum too small → high context switch overhead"
echo ""
echo -e "${YELLOW}[RULE OF THUMB]${NC} 80% of CPU bursts should be shorter than quantum"

read -p "Press Enter to continue..."

# ============================================================================
# 5. PRIORITY SCHEDULING
# ============================================================================
section "5. PRIORITY SCHEDULING"

# Define processes for Priority: (PID, Arrival Time, Burst Time, Priority)
declare -A processes_priority=(
    ["P1"]="0 10 3"
    ["P2"]="0 1 1"
    ["P3"]="0 2 4"
    ["P4"]="0 1 5"
    ["P5"]="0 5 2"
)

echo -e "${BOLD}Process List (lower number = higher priority):${NC}"
echo "┌──────┬──────────────┬────────────┬──────────┐"
echo "│ PID  │ Arrival Time │ Burst Time │ Priority │"
echo "├──────┼──────────────┼────────────┼──────────┤"
for pid in "${!processes_priority[@]}"; do
    read arrival burst priority <<< "${processes_priority[$pid]}"
    printf "│ %-4s │ %-12s │ %-10s │ %-8s │\n" "$pid" "$arrival" "$burst" "$priority"
done
echo "└──────┴──────────────┴────────────┴──────────┘"

echo -e "\n${BOLD}Priority Execution Order:${NC}"
{
    for pid in "${!processes_priority[@]}"; do
        read arrival burst priority <<< "${processes_priority[$pid]}"
        echo "$priority $burst $pid"
    done
} | sort -n | while read priority burst pid; do
    echo "  $pid (priority: $priority, burst: $burst ms)"
done

echo -e "\n${RED}⚠ STARVATION PROBLEM:${NC} Low-priority processes may never execute"
echo "${GREEN}✓ SOLUTION - AGING:${NC} Gradually increase priority of waiting processes"
echo "  Priority(t) = BasePriority + f(waiting_time)"
echo "  where f() increases with time"

read -p "Press Enter to continue..."

# ============================================================================
# 6. MULTILEVEL QUEUE SCHEDULING
# ============================================================================
section "6. MULTILEVEL QUEUE SCHEDULING"

echo -e "${BOLD}Multilevel Queue Structure:${NC}"
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo "│                    READY QUEUES                            │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${GREEN}QUEUE 0: Real-time processes${NC}                 │"
echo "│        Priority: Highest                                   │"
echo "│        Algorithm: Fixed Priority                           │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${YELLOW}QUEUE 1: System processes${NC}                   │"
echo "│        Priority: High                                      │"
echo "│        Algorithm: Round Robin (quantum=8ms)                │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${BLUE}QUEUE 2: Interactive processes${NC}                │"
echo "│        Priority: Medium                                    │"
echo "│        Algorithm: Round Robin (quantum=16ms)               │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${PURPLE}QUEUE 3: Batch processes${NC}                    │"
echo "│        Priority: Low                                       │"
echo "│        Algorithm: FCFS                                     │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""
explain "Each queue has its own scheduling algorithm"
explain "Processes don't move between queues (static assignment)"

echo -e "${BOLD}Queue Scheduling Policy:${NC}"
echo "1. Always run process from highest priority non-empty queue"
echo "2. Within a queue, use that queue's scheduling algorithm"
echo "3. Lower priority queues only run when higher queues are empty"

read -p "Press Enter to continue..."

# ============================================================================
# 7. MULTILEVEL FEEDBACK QUEUE
# ============================================================================
section "7. MULTILEVEL FEEDBACK QUEUE (MLFQ)"

echo -e "${BOLD}MLFQ - Dynamic Priority Adjustment:${NC}"
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo -e "│         ${CYAN}MLFQ with 3 Queues${NC}                     │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${GREEN}Q0: RR (quantum=8ms)${NC} - Highest priority      │"
echo "│      ↳ New jobs enter here                                 │"
echo "│      ↳ If job uses full quantum → demote to Q1             │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${YELLOW}Q1: RR (quantum=16ms)${NC} - Medium priority     │"
echo "│      ↳ If job uses full quantum → demote to Q2             │"
echo "│      ↳ If job blocks for I/O → promote to Q0               │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${RED}Q2: FCFS${NC} - Lowest priority                     │"
echo "│      ↳ CPU-bound jobs end up here                          │"
echo "│      ↳ No time slicing                                     │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""
explain "Processes can move between queues based on behavior"
explain "I/O-bound jobs stay in higher queues (good response)"
explain "CPU-bound jobs sink to lower queues (prevents hogging)"
explain "Aging: Boost priority of long-waiting jobs"

echo -e "${BOLD}MLFQ Rules Summary:${NC}"
echo "1. If Priority(A) > Priority(B), A runs"
echo "2. If Priority(A) = Priority(B), RR between A and B"
echo "3. New job enters highest priority queue"
echo "4. Job using full quantum → demoted"
echo "5. Job giving up CPU before quantum ends → stays same queue"
echo "6. After some time S, move all jobs to top queue (aging)"

read -p "Press Enter to continue..."

# ============================================================================
# 8. REAL-TIME SCHEDULING
# ============================================================================
section "8. REAL-TIME SCHEDULING"

echo -e "${BOLD}Types of Real-Time Systems:${NC}"
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo -e "│  ${RED}HARD REAL-TIME${NC}                                           │"
echo "│  • Missed deadline = system failure                         │"
echo "│  • Examples: Avionics, medical devices, automotive brakes  │"
echo "│  • Scheduling: Rate Monotonic, EDF (with feasibility test) │"
echo "├────────────────────────────────────────────────────────────┤"
echo -e "│  ${YELLOW}SOFT REAL-TIME${NC}                                         │"
echo "│  • Missed deadline = degraded performance                   │"
echo "│  • Examples: Multimedia, gaming, VoIP                       │"
echo "│  • Scheduling: Priority-based with timing constraints       │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

echo -e "${BOLD}Real-Time Scheduling Algorithms:${NC}"
echo ""
echo -e "1. ${GREEN}Rate Monotonic Scheduling (RMS)${NC}"
echo "   • Priority = 1 / Period"
echo "   • Shorter period = higher priority"
echo "   • Static priorities"
echo "   • Schedulable if: Σ(Ci/Ti) ≤ n(2^(1/n) - 1)"
echo ""
echo -e "2. ${GREEN}Earliest Deadline First (EDF)${NC}"
echo "   • Priority = earliest deadline"
echo "   • Dynamic priorities"
echo "   • Optimal for single processor"
echo "   • Schedulable if: Σ(Ci/Ti) ≤ 1"
echo ""
echo -e "3. ${GREEN}Proportional Share${NC}"
echo "   • Allocate shares/tokens"
echo "   • Process gets CPU proportion = its_shares / total_shares"
echo "   • Good for mixed workloads"

read -p "Press Enter to continue..."

# ============================================================================
# 9. LINUX SCHEDULER DEMONSTRATION
# ============================================================================
section "9. LINUX SCHEDULER IN ACTION"

echo -e "${BOLD}Linux Scheduler Evolution:${NC}"
echo ""
echo "┌────────────────────────────────────────────────────────────┐"
echo "│  Linux 2.4: O(n) scheduler                                 │"
echo "│  Linux 2.6: O(1) scheduler (2003)                          │"
echo "│  Linux 2.6.23: Completely Fair Scheduler - CFS (2007)      │"
echo "│  Current: CFS with real-time support                       │"
echo "└────────────────────────────────────────────────────────────┘"
echo ""

# Show current Linux scheduler info
echo -e "${BOLD}Current Scheduler Information:${NC}"
echo ""

# Check if we can access scheduler info
if [ -f /proc/sched_debug ]; then
    echo "Available scheduler classes:"
    grep -E "^[A-Z]" /proc/sched_debug | head -5
    echo ""
fi

# Show nice values and priorities
echo "Nice value range: -20 (highest priority) to +19 (lowest priority)"
echo "Real-time priority range: 1 (lowest) to 99 (highest)"
echo ""

# Show current process scheduling
echo -e "${BOLD}Current Process Scheduling (sample):${NC}"
ps -eo pid,comm,ni,pri,cls --sort=-ni | head -10 | awk '
BEGIN {
    printf "%-8s %-20s %-6s %-6s %-10s\n", "PID", "COMMAND", "NICE", "PRI", "CLASS"
    printf "%-8s %-20s %-6s %-6s %-10s\n", "------", "--------------------", "----", "---", "----------"
}
{
    printf "%-8s %-20s %-6s %-6s %-10s\n", $1, $2, $3, $4, $5
}'

echo ""
echo -e "${BOLD}CFS Red-Black Tree Visualization:${NC}"
echo ""
echo "           [vruntime=15]"
echo "           /            \\"
echo "  [vruntime=10]       [vruntime=20]"
echo "   /        \\               \\"
echo "[5]        [12]           [25]"
echo ""
explain "CFS stores tasks in red-black tree sorted by vruntime"
explain "Leftmost node (smallest vruntime) runs next"
explain "vruntime increases as task runs, moves it right in tree"
explain "I/O-bound tasks have small vruntime (stay left)"
explain "CPU-bound tasks have large vruntime (move right)"

read -p "Press Enter to continue..."

# ============================================================================
# 10. PRACTICAL EXAMPLES
# ============================================================================
section "10. PRACTICAL SCHEDULING EXAMPLES"

echo -e "${BOLD}Example 1: Setting Process Priority${NC}"
echo ""
echo "  # Set nice value (higher priority)"
echo -e "  ${GREEN}sudo nice -n -10 ./cpu_intensive_program${NC}"
echo ""
echo "  # Change nice value of running process"
echo -e "  ${GREEN}sudo renice -5 -p <PID>${NC}"
echo ""
echo "  # Set real-time priority (SCHED_FIFO)"
echo -e "  ${GREEN}sudo chrt -f -p 99 <PID>${NC}"
echo ""

echo -e "${BOLD}Example 2: CPU Affinity${NC}"
echo ""
echo "  # Run process on CPU 0 only"
echo -e "  ${GREEN}taskset -c 0 ./program${NC}"
echo ""
echo "  # Bind running process to CPUs 0-2"
echo -e "  ${GREEN}taskset -pc 0-2 <PID>${NC}"
echo ""

echo -e "${BOLD}Example 3: Stress Testing Scheduler${NC}"
echo ""
echo "  # Create CPU-bound processes"
echo -e "  ${GREEN}stress -c 4${NC}  # 4 CPU workers"
echo ""
echo "  # Create I/O-bound processes"
echo -e "  ${GREEN}stress -i 4${NC}  # 4 I/O workers"
echo ""
echo "  # Monitor scheduler behavior"
echo -e "  ${GREEN}watch -n 1 'ps -eo pid,comm,ni,pri,pcpu,psr | head -20'${NC}"

echo -e "\n${BOLD}Example 4: Scheduler Statistics${NC}"
echo ""
echo "  # Context switches per second"
echo -e "  ${GREEN}vmstat 1${NC}  # Look at 'cs' column"
echo ""
echo "  # CPU runqueue length"
echo -e "  ${GREEN}cat /proc/loadavg${NC}"
echo ""
echo "  # Detailed scheduler stats"
echo -e "  ${GREEN}cat /proc/schedstat | head -5${NC}"

read -p "Press Enter to continue..."

# ============================================================================
# FINAL SUMMARY
# ============================================================================
section "SCHEDULING ALGORITHM COMPARISON"

echo -e "${BOLD}Comparison Table:${NC}"
echo ""
echo "┌─────────────────┬────────────────┬─────────────────┬─────────────────┐"
echo "│ Algorithm       │ Avg Wait Time  │ Turnaround Time │ Response Time   │"
echo "├─────────────────┼────────────────┼─────────────────┼─────────────────┤"
echo "│ FCFS            │ High           │ High            │ High            │"
echo -e "│ SJF             │ ${GREEN}Optimal${NC}       │ Good            │ Poor             │"
echo "│ SRTF            │ Good           │ Good            │ ${GREEN}Good${NC}            │"
echo -e "│ Round Robin     │ Medium         │ Medium          │ ${GREEN}Excellent${NC}      │"
echo "│ Priority        │ Varies         │ Varies          │ Varies          │"
echo -e "│ Multilevel Q    │ Good           │ Good            │ ${GREEN}Excellent${NC}      │"
echo -e "│ Multilevel FQ   │ ${GREEN}Excellent${NC}     │ ${GREEN}Excellent${NC}      │ ${GREEN}Excellent${NC}      │"
echo "│ Real-Time       │ Predictable    │ Predictable     │ Guaranteed      │"
echo "└─────────────────┴────────────────┴─────────────────┴─────────────────┘"
echo ""

echo -e "${BOLD}Key Takeaways:${NC}"
echo -e "1. ${GREEN}FCFS${NC}: Simple but suffers from convoy effect"
echo -e "2. ${GREEN}SJF${NC}: Optimal for waiting time but needs burst prediction"
echo -e "3. ${GREEN}Round Robin${NC}: Fair, good for time-sharing systems"
echo -e "4. ${GREEN}Priority${NC}: Flexible but needs aging to prevent starvation"
echo -e "5. ${GREEN}Multilevel Feedback Queue${NC}: Balances response and throughput"
echo -e "6. ${GREEN}Real-Time${NC}: Provides timing guarantees for critical apps"
echo -e "7. ${GREEN}Linux CFS${NC}: Fair scheduling using vruntime and red-black trees"

echo -e "\n${CYAN}=================================================================="
echo -e "  END OF CPU SCHEDULING DEMONSTRATION"
echo -e "==================================================================${NC}\n"

echo -e "${BOLD}Try These Commands to Explore Further:${NC}"
echo -e "  ${GREEN}chrt -m${NC}           # Show min/max real-time priorities"
echo -e "  ${GREEN}taskset -p <PID>${NC}  # Show CPU affinity of process"
echo -e "  ${GREEN}ps -eo pid,comm,cls,rtprio,ni${NC}  # View scheduling classes"
echo -e "  ${GREEN}cat /proc/<PID>/sched${NC}  # Detailed scheduler info for process"
echo -e "  ${GREEN}perf sched record ./program${NC}  # Record scheduler events"

echo -e "\n${YELLOW}Happy Scheduling!${NC}\n"
