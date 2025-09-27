import time
from dataclasses import dataclass
from typing import Optional


class Job:
    def __init__(self, id, material, est_time, priority):
        self.id = id
        self.material = material
        self.est_time = est_time
        self.priority = priority
        self.created_at = time.time()
        self.status = 'queued'
        self.started_at = None
        self.completed_at = None

    def start_printing(self):
        self.status = 'started'
        self.started_at = time.time()
        print(f"Job {self.id} started printing at {self.started_at}")

    def complete_printing(self):
        self.status = 'completed'
        self.completed_at = time.time()
        print(f"Job {self.id} completed printing at {self.completed_at}")
    
    def get_wait_time(self):
        if self.started_at:
            return self.started_at - self.created_at
        return None
    
    def get_run_time(self):
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None
    
    def __str__(self):
        return f"Job({self.id}, {self.material}, {self.est_time}s, priority={self.priority})"


@dataclass
class Printer:
    id: int
    current_job: Optional[Job] = None
    is_busy: bool = False
    total_jobs_completed: int = 0
    total_busy_time: float = 0.0
    
    def start_job(self, job: Job):
        self.current_job = job
        self.is_busy = True
        job.start_printing()
    
    def complete_job(self):
        if self.current_job:
            self.current_job.complete_printing()
            
            self.total_jobs_completed += 1
            if self.current_job.get_run_time():
                self.total_busy_time += self.current_job.get_run_time()
            
            self.current_job = None
            self.is_busy = False
    
    def __str__(self):
        status = f"busy with {self.current_job.id}" if self.is_busy else "idle"
        return f"Printer-{self.id} ({status})"


if __name__ == "__main__":

    job1 = Job("My first job", "Plastic", 120, 1)
    print(f"Job created: {job1.id}")
    print(f"Initial status: {job1.status}")
    

    printer1 = Printer(id=1)
    print(f"\nPrinter created: {printer1}")
    print(f"Printer busy: {printer1.is_busy}")

    printer1.start_job(job1)
    print(f"After starting job: {printer1}")
    print(f"Job status: {job1.status}")
    
    time.sleep(2)
    

    printer1.complete_job()
    
    print(f"After completing job: {printer1}")
    print(f"Jobs completed: {printer1.total_jobs_completed}")
    print(f"Total busy time: {printer1.total_busy_time:.2f}s")
    
    print(f"\nJob waiting time: {job1.get_wait_time():.2f}s")
    print(f"Job exec time: {job1.get_run_time():.2f}s")