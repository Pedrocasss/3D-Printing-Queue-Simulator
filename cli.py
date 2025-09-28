import argparse
import sys
import json
import os
import time
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulator import PrinterSimulator
from models import Job

# File to persist state between commands
STATE_FILE = '.printer_cli_state.json'

class SimplePrinterCLI:
    def __init__(self, num_printers: int = 2, time_scale: float = 0.01):
        self.num_printers = num_printers
        self.time_scale = time_scale
        self.jobs_data = []
        self.load_state()
    
    def load_state(self):
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.jobs_data = data.get('jobs', [])
                    self.num_printers = data.get('num_printers', self.num_printers)
                    self.time_scale = data.get('time_scale', self.time_scale)
        except (json.JSONDecodeError, FileNotFoundError):
            self.jobs_data = []
    
    def save_state(self):
        state = {
            'jobs': self.jobs_data,
            'num_printers': self.num_printers,
            'time_scale': self.time_scale
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def add_job(self, job_id: str, material: str, est_time: float, priority: int):

        if any(job['id'] == job_id for job in self.jobs_data):
            print(f"Error: Job ID '{job_id}' already exists")
            return False
        
        
        if est_time <= 0:
            print("Error: Estimated time must be positive")
            return False
        
        if priority not in [1, 2, 3]:
            print("Error: Priority must be 1 (high), 2 (medium), or 3 (low)")
            return False
        
        job_data = {
            'id': job_id,
            'material': material,
            'est_time': est_time,
            'priority': priority,
            'created_at': time.time(),
            'status': 'queued'
        }
        
        self.jobs_data.append(job_data)
        self.save_state()
        
        print(f"Job '{job_id}' added successfully")
        print(f"  Material: {material}")
        print(f"  Estimated time: {est_time}s") 
        print(f"  Priority: {priority} ({'high' if priority == 1 else 'medium' if priority == 2 else 'low'})")
        return True
    
    def list_jobs(self):
        
        if not self.jobs_data:
            print("No jobs in queue")
            return
        
        queued = [j for j in self.jobs_data if j['status'] == 'queued']
        completed = [j for j in self.jobs_data if j['status'] == 'completed']
        cancelled = [j for j in self.jobs_data if j['status'] == 'cancelled']
        
        print(f"Queue Status:")
        print(f"  Total jobs: {len(self.jobs_data)}")
        print(f"  Queued: {len(queued)}")
        print(f"  Completed: {len(completed)}")
        print(f"  Cancelled: {len(cancelled)}")
        print(f"  Configuration: {self.num_printers} printers, time_scale={self.time_scale}")
        
        if queued:
            print(f"\nQueued Jobs:")
            
            queued_sorted = sorted(queued, key=lambda x: (x['priority'], x['created_at']))
            for i, job in enumerate(queued_sorted, 1):
                priority_name = {1: 'high', 2: 'medium', 3: 'low'}[job['priority']]
                print(f"  {i}. {job['id']} - {job['material']} - {job['est_time']}s - Priority: {job['priority']} ({priority_name})")
    
    def cancel_job(self, job_id: str):
        job_found = False
        for job in self.jobs_data:
            if job['id'] == job_id:
                job_found = True
                if job['status'] == 'queued':
                    job['status'] = 'cancelled'
                    self.save_state()
                    print(f"Job '{job_id}' cancelled successfully")
                    return True
                else:
                    print(f"Job '{job_id}' cannot be cancelled (status: {job['status']})")
                    return False
        
        if not job_found:
            print(f"Job '{job_id}' not found")
            return False
    
    def run_simulation(self, save_report: bool = True):
        if not self.jobs_data:
            print("No jobs to process")
            return
        
        queued_jobs = [j for j in self.jobs_data if j['status'] == 'queued']
        if not queued_jobs:
            print("No queued jobs to process")
            return
        
        print(f"Starting simulation...")
        print(f"  Jobs to process: {len(queued_jobs)}")
        print(f"  Printers: {self.num_printers}")
        print(f"  Time scale: {self.time_scale}")
        print()
        
        
        simulator = PrinterSimulator(num_printers=self.num_printers, time_scale=self.time_scale)
        
        
        jobs_to_run = []
        for job_data in queued_jobs:
            job = Job(
                id=job_data['id'],
                material=job_data['material'],
                est_time=job_data['est_time'],
                priority=job_data['priority']
            )
            job.created_at = job_data['created_at']  
            jobs_to_run.append(job)
            simulator.add_job(job)
        
        
        start_time = time.time()
        simulator.run_until_complete()
        duration = time.time() - start_time
        
        
        report = simulator.get_report()
        for job_report in report['jobs']:
            for job_data in self.jobs_data:
                if job_data['id'] == job_report['id']:
                    job_data['status'] = job_report['status']
                    job_data['started_at'] = job_report['started_at']
                    job_data['completed_at'] = job_report['completed_at']
                    break
        
        self.save_state()
        
        
        print(f"\nSimulation completed in {duration:.2f}s")
        final_status = simulator.get_status()
        print(f"  Completed: {final_status['completed']}")
        print(f"  Cancelled: {final_status['cancelled']}")
        
        
        if save_report:
            timestamp = int(time.time())
            json_filename = f"simulation_report_{timestamp}.json"
            csv_filename = f"simulation_report_{timestamp}.csv"
            
            simulator.save_report(json_filename, "json")
            simulator.save_report(csv_filename, "csv")
            
            print(f"\nReports saved:")
            print(f"  JSON: {json_filename}")
            print(f"  CSV: {csv_filename}")
        
       
        metrics = report['metrics']
        if metrics['completed_jobs'] > 0:
            print(f"\nMetrics Summary:")
            print(f"  Total simulation time: {metrics['simulation_duration_seconds']:.2f}s")
            if 'avg_wait_time' in metrics:
                print(f"  Average wait time: {metrics['avg_wait_time']:.3f}s")
            if 'throughput_jobs_per_second' in metrics:
                print(f"  Throughput: {metrics['throughput_jobs_per_second']:.2f} jobs/sec")
            if 'average_printer_utilization' in metrics:
                print(f"  Average printer utilization: {metrics['average_printer_utilization']:.1f}%")
    
    def clear_all(self):
        
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        self.jobs_data = []
        print("All jobs cleared")
    
    def load_jobs_from_file(self, filename: str):
        
        try:
            with open(filename, 'r') as f:
                jobs_data = json.load(f)
            
            added_count = 0
            for job_data in jobs_data:
                success = self.add_job(
                    job_data['id'],
                    job_data['material'], 
                    job_data['est_time'],
                    job_data['priority']
                )
                if success:
                    added_count += 1
            
            print(f"Loaded {added_count} jobs from {filename}")
            
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {filename}")
        except KeyError as e:
            print(f"Missing required field in job data: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="3D Printer Queue Simulator - Simple CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --id job1 --material PLA --time 120 --priority 1
  %(prog)s list
  %(prog)s cancel job1
  %(prog)s run
  %(prog)s load sample_jobs.json
  %(prog)s clear
        """
    )
    
    parser.add_argument('--printers', '-p', type=int, default=2,
                       help='Number of printers (default: 2)')
    parser.add_argument('--time-scale', '-t', type=float, default=0.01,
                       help='Time scale factor (default: 0.01)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    add_parser = subparsers.add_parser('add', help='Add a job to queue')
    add_parser.add_argument('--id', required=True, help='Unique job ID')
    add_parser.add_argument('--material', default='PLA', help='Material type (default: PLA)')
    add_parser.add_argument('--time', type=float, required=True, help='Estimated time in seconds')
    add_parser.add_argument('--priority', type=int, choices=[1, 2, 3], default=2,
                           help='Priority: 1=high, 2=medium, 3=low (default: 2)')
    
    subparsers.add_parser('list', help='List all jobs in queue')
    
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a job')
    cancel_parser.add_argument('job_id', help='ID of job to cancel')
    
    run_parser = subparsers.add_parser('run', help='Run simulation and generate report')
    run_parser.add_argument('--no-report', action='store_true', help='Skip saving report files')
    
    load_parser = subparsers.add_parser('load', help='Load jobs from JSON file')
    load_parser.add_argument('filename', help='JSON file with job data')
    

    subparsers.add_parser('clear', help='Clear all jobs')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SimplePrinterCLI(num_printers=args.printers, time_scale=args.time_scale)
    
    if args.command == 'add':
        cli.add_job(args.id, args.material, args.time, args.priority)
    
    elif args.command == 'list':
        cli.list_jobs()
    
    elif args.command == 'cancel':
        cli.cancel_job(args.job_id)
    
    elif args.command == 'run':
        cli.run_simulation(save_report=not args.no_report)
    
    elif args.command == 'load':
        cli.load_jobs_from_file(args.filename)
    
    elif args.command == 'clear':
        cli.clear_all()


if __name__ == "__main__":
    main()