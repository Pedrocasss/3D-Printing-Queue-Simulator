import threading
import time
import json
import csv
from typing import List, Dict, Optional
from models import Job, Printer
from queue_manager import JobQueue


class PrinterSimulator:
    def __init__(self, num_printers: int = 2, time_scale: float = 0.01):
        self.num_printers = num_printers
        self.time_scale = time_scale
        
        self.job_queue = JobQueue()
        self.printers = [Printer(id=i) for i in range(num_printers)]
        
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.worker_threads: List[threading.Thread] = []
        
        self.all_jobs: Dict[str, Job] = {}
        self.completed_jobs: List[Job] = []
        self.cancelled_jobs: List[Job] = []
        
        self.simulation_start_time: Optional[float] = None
        self.simulation_end_time: Optional[float] = None
        
        print(f"PrinterSimulator created with {num_printers} printers, time_scale={time_scale}")
    
    def add_job(self, job: Job) -> None:
        with self.lock:
            self.all_jobs[job.id] = job
            self.job_queue.add_job(job)
    
    def cancel_job(self, job_id: str) -> bool:
        with self.lock:
            if job_id not in self.all_jobs:
                print(f"Job {job_id} not found")
                return False
            
            job = self.all_jobs[job_id]
            
            if job.status == 'queued':
                if self.job_queue.cancel_job(job_id):
                    self.cancelled_jobs.append(job)
                    return True
            elif job.status == 'started':
                print(f"Job {job_id} is running, cannot cancel")
                return False
            else:
                print(f"Job {job_id} status is {job.status}, cannot cancel")
                return False
    
    def _printer_worker(self, printer: Printer) -> None:
        print(f"Printer-{printer.id} worker started")
        
        while not self.stop_event.is_set():
            job = self.job_queue.get_next_job()
            
            if job is None:
                time.sleep(0.1)
                continue
            
            if job.status == 'cancelled':
                continue
            
            with self.lock:
                printer.start_job(job)
            
            print(f"Printer-{printer.id} processing {job.id} (scaled_time={job.est_time * self.time_scale:.2f}s)")
            
            time.sleep(job.est_time * self.time_scale)
            
            with self.lock:
                printer.complete_job()
                self.completed_jobs.append(job)
            
            print(f"Printer-{printer.id} completed {job.id}")
        
        print(f"Printer-{printer.id} worker stopped")
    
    def start_simulation(self) -> None:
        if self.worker_threads:
            print("Simulation already running")
            return
        
        self.simulation_start_time = time.time()
        self.stop_event.clear()
        
        for printer in self.printers:
            thread = threading.Thread(
                target=self._printer_worker,
                args=(printer,),
                name=f"Printer-{printer.id}",
                daemon=True
            )
            thread.start()
            self.worker_threads.append(thread)
        
        print(f"Simulation started with {self.num_printers} printers")
    
    def stop_simulation(self) -> None:
        if not self.worker_threads:
            print("No simulation running")
            return
        
        print("Stopping simulation...")
        self.stop_event.set()
        
        for thread in self.worker_threads:
            thread.join(timeout=5.0)
        
        self.worker_threads.clear()
        self.simulation_end_time = time.time()
        print("Simulation stopped")
    
    def run_until_complete(self, timeout: Optional[float] = None) -> None:
        self.start_simulation()
        
        start_wait = time.time()
        
        try:
            while True:
                with self.lock:
                    total_jobs = len(self.all_jobs)
                    finished_jobs = len(self.completed_jobs) + len(self.cancelled_jobs)
                    
                    if finished_jobs >= total_jobs and self.job_queue.is_empty():
                        break
                
                if timeout and (time.time() - start_wait) > timeout:
                    print(f"Timeout reached ({timeout}s)")
                    break
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("Simulation interrupted")
        finally:
            self.stop_simulation()
    
    def get_status(self) -> Dict:
        with self.lock:
            running_jobs = [job for job in self.all_jobs.values() if job.status == 'started']
            queued_jobs = [job for job in self.all_jobs.values() if job.status == 'queued']
            
            return {
                'total_jobs': len(self.all_jobs),
                'queued': len(queued_jobs),
                'running': len(running_jobs),
                'completed': len(self.completed_jobs),
                'cancelled': len(self.cancelled_jobs),
                'queue_size': self.job_queue.get_queue_size(),
                'active_printers': sum(1 for p in self.printers if p.is_busy)
            }
    
    def _calculate_metrics(self) -> Dict:
        if not self.completed_jobs:
            return {}
        
        wait_times = []
        run_times = []
        
        for job in self.completed_jobs:
            wait_time = job.get_wait_time()
            run_time = job.get_run_time()
            if wait_time is not None:
                wait_times.append(wait_time)
            if run_time is not None:
                run_times.append(run_time)
        
        sim_duration = 0
        if self.simulation_start_time and self.simulation_end_time:
            sim_duration = self.simulation_end_time - self.simulation_start_time
        
        metrics = {
            'total_jobs': len(self.all_jobs),
            'completed_jobs': len(self.completed_jobs),
            'cancelled_jobs': len(self.cancelled_jobs),
            'simulation_duration_seconds': sim_duration,
            'time_scale_factor': self.time_scale
        }
        
        if wait_times:
            metrics.update({
                'avg_wait_time': sum(wait_times) / len(wait_times),
                'median_wait_time': sorted(wait_times)[len(wait_times) // 2],
                'max_wait_time': max(wait_times),
                'min_wait_time': min(wait_times)
            })
        
        if run_times:
            metrics['avg_run_time'] = sum(run_times) / len(run_times)
        
        if sim_duration > 0:
            metrics['throughput_jobs_per_second'] = len(self.completed_jobs) / sim_duration
        
        printer_utilization = {}
        for printer in self.printers:
            if sim_duration > 0:
                utilization = printer.total_busy_time / sim_duration
            else:
                utilization = 0
            
            printer_utilization[f'printer_{printer.id}'] = {
                'jobs_completed': printer.total_jobs_completed,
                'total_busy_time': printer.total_busy_time,
                'utilization_percentage': utilization * 100
            }
        
        metrics['printer_utilization'] = printer_utilization
        return metrics
    
    def get_report(self) -> Dict:
        job_reports = []
        
        for job in self.all_jobs.values():
            job_report = {
                'id': job.id,
                'material': job.material,
                'est_time': job.est_time,
                'priority': job.priority,
                'status': job.status,
                'created_at': job.created_at,
                'started_at': job.started_at,
                'completed_at': job.completed_at,
                'wait_time': job.get_wait_time(),
                'run_time': job.get_run_time()
            }
            job_reports.append(job_report)
        
        job_reports.sort(key=lambda x: x['started_at'] or 0)
        
        return {
            'jobs': job_reports,
            'metrics': self._calculate_metrics(),
            'simulation_config': {
                'num_printers': self.num_printers,
                'time_scale': self.time_scale
            }
        }
    
    def save_report(self, filename: str, format_type: str = 'json') -> None:
        report = self.get_report()
        
        if format_type.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"JSON report saved to {filename}")
        
        elif format_type.lower() == 'csv':
            with open(filename, 'w', newline='') as f:
                if report['jobs']:
                    writer = csv.DictWriter(f, fieldnames=report['jobs'][0].keys())
                    writer.writeheader()
                    writer.writerows(report['jobs'])
            print(f"CSV report saved to {filename}")
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")


if __name__ == "__main__":
    sim = PrinterSimulator(num_printers=2, time_scale=0.5)
    jobs = [
        Job("urgent_job_1", "PLASTIC 1", 3, 1),
        Job("urgent_job_2", "PLASTIC 2", 4, 1),
        Job("normal_job_1", "PLASTIC 3", 2, 2),
        Job("normal_job_2", "PLASTIC 4", 5, 2),
        Job("low_job_1", "PLASTIC 5", 2, 3),
        Job("low_job_2", "PLASTIC 6", 3, 3),
        Job("urgent_job_3", "PLASTIC 7", 2, 1),
    ]
    for job in jobs: sim.add_job(job)

    print("\nInitial status:", sim.get_status())
    sim.start_simulation()

    for i in range(16):
        time.sleep(0.5)
        s = sim.get_status()
        print(f"t={i*0.5:.1f}s - Queued:{s['queued']}, Running:{s['running']}, Completed:{s['completed']}")

        if i == 8:
            r = sim.get_report()
            sim.save_report("intermediate_report.csv", "csv")
            print("\n--- Intermediate Report (4s) ---")
            for j in r['jobs']: print(f"  {j['id']}: {j['status']}")
            print("--- Saved intermediate_report.csv ---\n")

        if not s['queued'] and not s['running']:
            print("All jobs finished!")
            break

    sim.stop_simulation()
    print("\nFinal status:", sim.get_status())

    sim.save_report("simulation_report.json", "json")
    sim.save_report("simulation_report.csv", "csv")
    r = sim.get_report()

    print(f"\nFinal Summary:\nTotal jobs: {r['metrics']['total_jobs']}\n"
          f"Completed: {r['metrics']['completed_jobs']}\n"
          f"Simulation time: {r['metrics']['simulation_duration_seconds']:.2f}s")

    print("\nFinal job statuses:")
    for j in r['jobs']: print(f"  {j['id']}: {j['status']}")

    m = r['metrics']
    if 'avg_wait_time' in m: print(f"\nAverage wait time: {m['avg_wait_time']:.3f}s")
    if 'throughput_jobs_per_second' in m: print(f"Throughput: {m['throughput_jobs_per_second']:.2f} jobs/sec")
