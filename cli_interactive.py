import argparse
import sys
import json
import time
from typing import Optional

import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from simulator import PrinterSimulator
from models import Job


class PrinterCLI:
    def __init__(self):
        self.simulator: Optional[PrinterSimulator] = None
        self.jobs_file = "jobs.json"
        self.default_printers = 2
        self.default_time_scale = 0.01
    
    def create_simulator(self, num_printers: int = None, time_scale: float = None):
        num_printers = num_printers or self.default_printers
        time_scale = time_scale or self.default_time_scale
        
        self.simulator = PrinterSimulator(num_printers=num_printers, time_scale=time_scale)
        print(f"Simulator created: {num_printers} printers, time_scale={time_scale}")
    
    def configure_simulator(self):
        print(f"\nSimulator Configuration")
        try:
            printers_input = input(f"Number of printers (current: {self.default_printers}): ").strip()
            if printers_input:
                new_printers = int(printers_input)
                if new_printers < 1:
                    print("Number of printers must be at least 1")
                    return
                self.default_printers = new_printers
            
            time_scale_input = input(f"Time scale factor (current: {self.default_time_scale}): ").strip()
            if time_scale_input:
                new_time_scale = float(time_scale_input)
                if new_time_scale <= 0:
                    print("Time scale must be positive")
                    return
                self.default_time_scale = new_time_scale
            
            self.create_simulator()
            print(f"Configuration updated!")
            
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    def add_job(self, job_id: str, material: str, est_time: float, priority: int):

        if not self.simulator:
            self.create_simulator()
        
        job = Job(job_id, material, est_time, priority)
        self.simulator.add_job(job)
        print(f"Job '{job_id}' added to queue")
        print(f"   Material: {material}, Time: {est_time}s, Priority: {priority}")
    
    def list_queue(self):

        if not self.simulator:
            print("No simulator created. Add jobs first or create simulator.")
            return
        
        status = self.simulator.get_status()
        print(f"\nQueue Status:")
        print(f"   Total jobs: {status['total_jobs']}")
        print(f"   Queued: {status['queued']}")
        print(f"   Running: {status['running']}")
        print(f"   Completed: {status['completed']}")
        print(f"   Cancelled: {status['cancelled']}")
        print(f"   Active printers: {status['active_printers']}")
        
        if status['queued'] > 0:
            print(f"\nJobs in queue:")
            queued_jobs = self.simulator.job_queue.jobs
            for i, job in enumerate(queued_jobs, 1):
                print(f"   {i}. {job.id} - Priority {job.priority} - {job.material} ({job.est_time}s)")
        
        if status['running'] > 0:
            print(f"\nCurrently printing:")
            for printer in self.simulator.printers:
                if printer.is_busy:
                    job = printer.current_job
                    print(f"   Printer-{printer.id}: {job.id} ({job.material})")
    
    def cancel_job(self, job_id: str):
        if not self.simulator:
            print("No simulator created.")
            return
        
        success = self.simulator.cancel_job(job_id)
        if success:
            print(f"Job '{job_id}' cancelled")
        else:
            print(f"Job '{job_id}' not found or cannot be cancelled")
    
    def run_simulation(self, timeout: Optional[float] = None):

        if not self.simulator:
            print("No simulator created. Add jobs first.")
            return
        
        status = self.simulator.get_status()
        if status['total_jobs'] == 0:
            print("No jobs to process. Add jobs first.")
            return
        
        print(f"Starting simulation...")
        print(f"   Jobs to process: {status['queued']}")
        print(f"   Printers available: {len(self.simulator.printers)}")
        
        start_time = time.time()
        self.simulator.run_until_complete(timeout=timeout)
        duration = time.time() - start_time
        
        print(f"\nSimulation completed in {duration:.2f}s")
        
        final_status = self.simulator.get_status()
        print(f"   Completed: {final_status['completed']}")
        print(f"   Cancelled: {final_status['cancelled']}")
    
    def show_report(self, save_json: bool = False, save_csv: bool = False):
        if not self.simulator:
            print("No simulator created.")
            return
        
        report = self.simulator.get_report()
        
        print(f"\nSimulation Report:")
        print(f"=" * 50)
        

        completed_jobs = [j for j in report['jobs'] if j['status'] == 'completed']
        if completed_jobs:
            print(f"\nCompleted Jobs ({len(completed_jobs)}):")
            for job in completed_jobs:
                wait = job['wait_time'] or 0
                run = job['run_time'] or 0
                print(f"   {job['id']}: waited {wait:.3f}s, ran {run:.3f}s")
        

        metrics = report['metrics']
        print(f"\nMetrics:")
        print(f"   Total jobs: {metrics['total_jobs']}")
        print(f"   Completed: {metrics['completed_jobs']}")
        print(f"   Cancelled: {metrics['cancelled_jobs']}")
        print(f"   Simulation time: {metrics['simulation_duration_seconds']:.3f}s")
        
        if 'avg_wait_time' in metrics:
            print(f"   Avg wait time: {metrics['avg_wait_time']:.3f}s")
        if 'throughput_jobs_per_second' in metrics:
            print(f"   Throughput: {metrics['throughput_jobs_per_second']:.2f} jobs/sec")
        
        if 'printer_utilization' in metrics:
            print(f"\nPrinter Utilization:")
            for printer_id, util in metrics['printer_utilization'].items():
                print(f"   {printer_id}: {util['utilization_percentage']:.1f}% "
                      f"({util['jobs_completed']} jobs)")
        
        if save_json:
            filename = f"report_{int(time.time())}.json"
            self.simulator.save_report(filename, "json")
            print(f"\nJSON report saved: {filename}")
        
        if save_csv:
            filename = f"report_{int(time.time())}.csv"
            self.simulator.save_report(filename, "csv")
            print(f"CSV report saved: {filename}")
    
    def load_jobs_from_file(self, filename: str):
        try:
            with open(filename, 'r') as f:
                jobs_data = json.load(f)
            
            if not self.simulator:
                self.create_simulator()
            
            for job_data in jobs_data:
                job = Job(
                    job_data['id'],
                    job_data['material'],
                    job_data['est_time'],
                    job_data['priority']
                )
                self.simulator.add_job(job)
            
            print(f"Loaded {len(jobs_data)} jobs from {filename}")
        
        except FileNotFoundError:
            print(f"File not found: {filename}")
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {filename}")
        except KeyError as e:
            print(f"Missing required field in job data: {e}")
    
    def show_status(self):
        if self.simulator:
            status = self.simulator.get_status()
            print(f"\nSimulator Status:")
            print(f"   Printers: {self.simulator.num_printers}")
            print(f"   Time scale: {self.simulator.time_scale}")
            print(f"   Total jobs: {status['total_jobs']}")
            print(f"   Queue: {status['queued']}, Running: {status['running']}")
            print(f"   Completed: {status['completed']}, Cancelled: {status['cancelled']}")
        else:
            print(f"\nNo simulator created")
            print(f"Default configuration: {self.default_printers} printers, time_scale={self.default_time_scale}")
    
    def interactive_mode(self):
        print(f"\nInteractive Mode - 3D Printer Simulator")
        print("Commands: add, list, cancel, run, report, config, status, quit")
        print("Type 'help' for detailed commands")
        
        if self.default_printers == 2 and self.default_time_scale == 0.01:
            print(f"\nCurrent defaults: {self.default_printers} printers, time_scale={self.default_time_scale}")
            change_config = input("Change configuration? (y/n): ").strip().lower()
            
            if change_config == 'y':
                self.configure_simulator()
            else:
                self.create_simulator()
        else:
            self.create_simulator()
        
        while True:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == 'quit' or cmd == 'exit':
                    print("Goodbye!")
                    break
                
                elif cmd == 'help':
                    print("\nAvailable commands:")
                    print("  add    - Add a new job interactively")
                    print("  list   - Show current queue status")
                    print("  cancel - Cancel a job by ID")
                    print("  run    - Run the simulation")
                    print("  report - Show detailed report")
                    print("  load   - Load jobs from JSON file")
                    print("  config - Reconfigure printers/time_scale")
                    print("  status - Show current simulator config")
                    print("  reset  - Reset simulator (keeps current config)")
                    print("  clear  - Clear all jobs and reset")
                    print("  quit   - Exit interactive mode")
                
                elif cmd == 'config':
                    self.configure_simulator()
                
                elif cmd == 'status':
                    self.show_status()
                
                elif cmd == 'reset':
                    if self.simulator:
                        current_printers = self.simulator.num_printers
                        current_time_scale = self.simulator.time_scale
                        self.create_simulator(current_printers, current_time_scale)
                        print("Simulator reset with same configuration")
                    else:
                        self.create_simulator()
                
                elif cmd == 'add':
                    if not self.simulator:
                        self.create_simulator()
                    
                    job_id = input("Job ID: ").strip()
                    material = input("Material (PLA/ABS/PETG): ").strip() or "PLA"
                    est_time = float(input("Estimated time (seconds): ").strip() or "60")
                    priority = int(input("Priority (1=high, 2=medium, 3=low): ").strip() or "2")
                    self.add_job(job_id, material, est_time, priority)
                
                elif cmd == 'list':
                    self.list_queue()
                
                elif cmd == 'cancel':
                    job_id = input("Job ID to cancel: ").strip()
                    self.cancel_job(job_id)
                
                elif cmd == 'run':
                    self.run_simulation()
                
                elif cmd == 'report':
                    self.show_report()

                elif cmd == 'load':
                    filename = input("JSON filename: ").strip()
                    self.load_jobs_from_file(filename)
                
                elif cmd == 'clear':
                    self.create_simulator()
                    print("Simulator reset")
                
                elif cmd == '':
                    continue
                
                else:
                    print(f"Unknown command: {cmd}. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="3D Printer Queue Simulator CLI")
    parser.add_argument('--printers', '-p', type=int, default=2, 
                       help='Number of printers (default: 2)')
    parser.add_argument('--time-scale', '-t', type=float, default=0.01,
                       help='Time scale factor (default: 0.01)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    add_parser = subparsers.add_parser('add', help='Add a job to queue')
    add_parser.add_argument('--id', required=True, help='Job ID')
    add_parser.add_argument('--material', default='PLA', help='Material type')
    add_parser.add_argument('--time', type=float, required=True, help='Estimated time in seconds')
    add_parser.add_argument('--priority', type=int, default=2, help='Priority (1=high, 2=medium, 3=low)')
    
    subparsers.add_parser('list', help='List jobs in queue')
    
    cancel_parser = subparsers.add_parser('cancel', help='Cancel a job')
    cancel_parser.add_argument('job_id', help='Job ID to cancel')
    
    run_parser = subparsers.add_parser('run', help='Run simulation')
    run_parser.add_argument('--timeout', type=float, help='Timeout in seconds')
    

    report_parser = subparsers.add_parser('report', help='Show simulation report')
    report_parser.add_argument('--json', action='store_true', help='Save JSON report')
    report_parser.add_argument('--csv', action='store_true', help='Save CSV report')
    
    load_parser = subparsers.add_parser('load', help='Load jobs from JSON file')
    load_parser.add_argument('filename', help='JSON file with job data')
    
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    args = parser.parse_args()
    
    cli = PrinterCLI()
    cli.default_printers = args.printers
    cli.default_time_scale = args.time_scale
    
    if args.command == 'add':
        cli.create_simulator(args.printers, args.time_scale)
        cli.add_job(args.id, args.material, args.time, args.priority)
    
    elif args.command == 'list':
        cli.list_queue()
    
    elif args.command == 'cancel':
        cli.cancel_job(args.job_id)
    
    elif args.command == 'run':
        cli.run_simulation(args.timeout)
    
    elif args.command == 'report':
        cli.show_report(args.json, args.csv)
    
    elif args.command == 'load':
        cli.load_jobs_from_file(args.filename)
    
    elif args.command == 'interactive':
        cli.interactive_mode()
    
    else:
        print("No command specified. Starting interactive mode...")
        cli.interactive_mode()


if __name__ == "__main__":
    main()