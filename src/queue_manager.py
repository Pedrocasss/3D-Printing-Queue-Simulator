import threading
from models import Job

class JobQueue:

    def __init__(self):
        self.jobs = []
        self._lock = threading.Lock()
        self._auto_sort = True
        self.counter = 0
    
    def add_job(self, job):
        with self._lock:
            self.counter += 1
            job.order_counter = self.counter
            self.jobs.append(job)
            if self._auto_sort:
                self._sort_by_priority_unsafe()
            print(f"Job '{job.id}' added.")
    
    def get_next_job(self):
        with self._lock:
            if self.jobs:
                # Re-sort before getting next job to ensure consistency
                self._sort_by_priority_unsafe()
                job = self.jobs.pop(0)
                print(f"Job {job.id} removed from queue.")
                return job
            else:
                print(f"No more jobs in the queue.")
                return None
    
    def sort_by_priority(self):
        with self._lock:
            self._sort_by_priority_unsafe()

    def _sort_by_priority_unsafe(self):
        self.jobs.sort(key=lambda job: (job.priority, job.order_counter))
    

    def list_jobs(self):
        with self._lock:
            if not self.jobs:
                print("Empty queue")
                return
            
            print("Current jobs in queue:")
            for i, job in enumerate(self.jobs, 1):
                print(f"  {i}. {job.id} - Priority {job.priority} - {job.material}")

    def get_queue_size(self):
        with self._lock:
            return len(self.jobs)

    def cancel_job(self, job_id):
        with self._lock:
            for i, job in enumerate(self.jobs):
                if job.id == job_id:
                    removed_job = self.jobs.pop(i)
                    removed_job.status = 'cancelled'
                    print(f"Job {job_id} cancelled and removed from queue.")
                    return True
            print(f"Job {job_id} not found in queue.")
            return False

    def is_empty(self):
        with self._lock:
            return len(self.jobs) == 0

    def peek_next_job(self):
        with self._lock:
            if self.jobs:
                return self.jobs[0]

if __name__ == "__main__":
    queue = JobQueue()

    job1 = Job("JOB1", "Plastic 1", 60, 1)
    job2 = Job("JOB2", "Plastic 2", 20, 1) 
    job3 = Job("JOB3", "Plastic 2", 45, 3)

    queue.add_job(job1)
    queue.add_job(job2)
    queue.add_job(job3)

    print(f"\nQueue size: {queue.get_queue_size()}")

    print("\n--- Priority order (auto-sorted) ---")
    queue.list_jobs()

    print("\n--- Processing jobs ---")
    while queue.get_queue_size() > 0:
        next_job = queue.get_next_job()
        print(f"Processing: {next_job}")

    print("\n--- Testing cancellation ---")
    job4 = Job("JOB4", "PLASTIC 4", 30, 2)
    job5 = Job("JOB5", "PLastic 5", 40, 1)
    
    queue.add_job(job4)
    queue.add_job(job5)
    
    print("\nBefore cancellation:")
    queue.list_jobs()
    
    queue.cancel_job("JOB4")
    
    print("\nAfter cancellation:")
    queue.list_jobs()