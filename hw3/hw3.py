import argparse
import csv

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        
        # Timestamps and metrics
        self.completion_time = 0
        self.first_run_time = -1
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0


def compute_metrics(processes):
    for p in processes:
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time
        p.response_time = p.first_run_time - p.arrival_time
    return processes


# --- 1. FCFS ---
def simulate_fcfs(processes):
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    procs.sort(key=lambda p: (p.arrival_time, p.pid))
    current_time = 0
    for p in procs:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
        p.first_run_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
    return compute_metrics(procs)


# --- 2. SJF (Non-Preemptive) ---
def simulate_sjf(processes):
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    n = len(procs)
    completed = []
    current_time = 0
    while len(completed) < n:
        available = [p for p in procs if p.arrival_time <= current_time and p not in completed]
        if not available:
            not_completed = [p for p in procs if p not in completed]
            next_proc = min(not_completed, key=lambda p: p.arrival_time)
            current_time = next_proc.arrival_time
            continue
        available.sort(key=lambda p: (p.burst_time, p.arrival_time, p.pid))
        p = available[0]
        p.first_run_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
        completed.append(p)
    return compute_metrics(procs)


# --- 3. Round Robin ---
def simulate_rr(processes, time_quantum=2):
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    remaining_burst = {p.pid: p.burst_time for p in procs}
    current_time = 0
    ready_queue = []
    unvisited = sorted(procs, key=lambda p: (p.arrival_time, p.pid))
    
    while unvisited or ready_queue:
        while unvisited and unvisited[0].arrival_time <= current_time:
            ready_queue.append(unvisited.pop(0))
        if not ready_queue:
            current_time = unvisited[0].arrival_time
            continue
        p = ready_queue.pop(0)
        if p.first_run_time == -1:
            p.first_run_time = current_time
        exec_time = min(time_quantum, remaining_burst[p.pid])
        remaining_burst[p.pid] -= exec_time
        current_time += exec_time
        while unvisited and unvisited[0].arrival_time <= current_time:
            ready_queue.append(unvisited.pop(0))
        if remaining_burst[p.pid] > 0:
            ready_queue.append(p)
        else:
            p.completion_time = current_time
    return compute_metrics(procs)


# --- 4. Priority (Non-Preemptive) ---
def simulate_priority(processes):
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    n = len(procs)
    completed = []
    current_time = 0
    while len(completed) < n:
        available = [p for p in procs if p.arrival_time <= current_time and p not in completed]
        if not available:
            not_completed = [p for p in procs if p not in completed]
            next_proc = min(not_completed, key=lambda p: p.arrival_time)
            current_time = next_proc.arrival_time
            continue
        available.sort(key=lambda p: (p.priority, p.arrival_time, p.pid))
        p = available[0]
        p.first_run_time = current_time
        current_time += p.burst_time
        p.completion_time = current_time
        completed.append(p)
    return compute_metrics(procs)


# --- 5. MLFQ (With Verbose Trace Option) ---
def simulate_mlfq(processes, num_queues=2, base_quantum=4, verbose=False):
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    remaining_burst = {p.pid: p.burst_time for p in procs}
    current_time = 0
    queues = [[] for _ in range(num_queues)]
    unvisited = sorted(procs, key=lambda p: (p.arrival_time, p.pid))
    
    if verbose:
        print(f"\nAlgorithm: MLFQ Trace Log")
        print(f"{'Time':<8}{'PID':<8}{'Queue':<8}{'Action'}")
        print("-" * 50)
    
    while unvisited or any(queues):
        while unvisited and unvisited[0].arrival_time <= current_time:
            queues[0].append(unvisited.pop(0))
            
        active_q_idx = -1
        for i in range(num_queues):
            if queues[i]:
                active_q_idx = i
                break
                
        if active_q_idx == -1:
            current_time = unvisited[0].arrival_time
            continue
            
        p = queues[active_q_idx].pop(0)
        if p.first_run_time == -1:
            p.first_run_time = current_time
            
        quantum = base_quantum * (2 ** active_q_idx)
        exec_time = min(quantum, remaining_burst[p.pid])
        
        start_t = current_time
        remaining_burst[p.pid] -= exec_time
        current_time += exec_time
        
        if remaining_burst[p.pid] > 0:
            action = f"Runs full quantum ({quantum}) -> demoted to Q{min(active_q_idx + 1, num_queues - 1)}"
        else:
            action = f"Finishes at t={current_time}"
            
        if verbose:
            print(f"{start_t:<8}{p.pid:<8}{f'Q{active_q_idx}':<8}{action}")
        
        while unvisited and unvisited[0].arrival_time <= current_time:
            queues[0].append(unvisited.pop(0))
            
        if remaining_burst[p.pid] > 0:
            next_q = min(active_q_idx + 1, num_queues - 1)
            queues[next_q].append(p)
        else:
            p.completion_time = current_time
            
    if verbose:
        print("-" * 50)
        res = compute_metrics(procs)
        avg_wt = sum(p.waiting_time for p in res) / len(res)
        print(f"Average Waiting Time:    {avg_wt:.2f}\n")
        
    return compute_metrics(procs)


# --- Unified Pluggable Dispatcher ---
def schedule(processes, algo_name, quantum=2):
    algo = algo_name.lower()
    if algo == "fcfs":
        return simulate_fcfs(processes)
    elif algo == "sjf":
        return simulate_sjf(processes)
    elif algo == "rr":
        return simulate_rr(processes, time_quantum=quantum)
    elif algo == "priority":
        return simulate_priority(processes)
    elif algo == "mlfq":
        return simulate_mlfq(processes, num_queues=2, base_quantum=4, verbose=False)
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")


# --- CSV Loader ---
def load_workload_from_csv(file_path):
    procs = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            pid = row.get('pid', 'P1')
            arrival = int(row.get('arrival_time', 0))
            burst = int(row.get('burst_time', 1))
            priority = int(row.get('priority', 0))
            procs.append(Process(pid, arrival, burst, priority))
    return procs


# --- Detailed Table Printer ---
def print_process_table(algo_name, processes):
    print(f"\nAlgorithm: {algo_name}")
    print(f"{'PID':<6}{'Arrival':<9}{'Burst':<7}{'Priority':<10}{'Start':<8}{'Completion':<12}{'Waiting':<10}{'Turnaround'}")
    print("-" * 72)
    for p in processes:
        start_time = p.first_run_time
        print(f"{p.pid:<6}{p.arrival_time:<9}{p.burst_time:<7}{p.priority:<10}{start_time:<8}{p.completion_time:<12}{p.waiting_time:<10}{p.turnaround_time}")
    
    avg_wt = sum(p.waiting_time for p in processes) / len(processes)
    avg_tat = sum(p.turnaround_time for p in processes) / len(processes)
    
    print("-" * 72)
    print(f"Average Waiting Time:    {avg_wt:.2f}")
    print(f"Average Turnaround Time: {avg_tat:.2f}\n")


# --- Comparison Report Generator ---
def generate_comparison_report(workload):
    algorithms = ["fcfs", "sjf", "rr", "priority", "mlfq"]
    
    print("=" * 65)
    print(f"{'Algorithm Comparison Report':^65}")
    print("=" * 65)
    print(f"{'Algorithm':<15}{'Avg Waiting Time':<20}{'Avg Turnaround':<20}{'Avg Response'}")
    print("-" * 65)
    
    for name in algorithms:
        result_procs = schedule(workload, name)
        avg_wt = sum(p.waiting_time for p in result_procs) / len(result_procs)
        avg_tat = sum(p.turnaround_time for p in result_procs) / len(result_procs)
        avg_rt = sum(p.response_time for p in result_procs) / len(result_procs)
        
        print(f"{name.upper():<15}{avg_wt:<20.2f}{avg_tat:<20.2f}{avg_rt:<.2f}")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CPU Scheduler Simulator")
    parser.add_argument("--workload", type=str, help="Path to workload CSV file")
    parser.add_argument("--algo", type=str, help="Algorithm to run (fcfs, sjf, rr, priority, mlfq)")
    parser.add_argument("--compare", action="store_true", help="Run full algorithm comparison report")
    parser.add_argument("--quantum", type=int, default=2, help="Time quantum for RR/MLFQ")
    
    args = parser.parse_args()

    # Load from CSV if specified, otherwise use default lecture workload
    if args.workload:
        workload = load_workload_from_csv(args.workload)
    else:
        workload = [
            Process("P1", 0, 6, priority=1),
            Process("P2", 0, 2, priority=3),
            Process("P3", 0, 8, priority=2),
            Process("P4", 0, 3, priority=3)
        ]
    
    if args.algo:
        algo_name = args.algo.lower()
        if algo_name == "mlfq":
            simulate_mlfq(workload, num_queues=2, base_quantum=4, verbose=True)
        else:
            res = schedule(workload, algo_name, quantum=args.quantum)
            print_process_table(algo_name.upper(), res)
    elif args.compare:
        generate_comparison_report(workload)
    else:
        generate_comparison_report(workload)
