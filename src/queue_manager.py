from models import Job

class JobQueue:

    def __init__(self):
        self.jobs=[]
    
    def add_job(self, job):

        self.jobs.append(job)
        print(f"Job '{job.id}' added.")
    
    def get_next_job(self):
        """ Im pretty sure that .pop is so slow but ok its just for testing right now."""
        
        if self.jobs:
            job = self.jobs.pop(0)
            print(f"Job {job.id} removed from queue.")
            return job
        else:
            print(f"No more jobs in the queue.")
            return None
    
    def sort_by_priority(self):
        
        self.jobs.sort(key=lambda job: job.priority)

    def list_jobs(self):
        if not self.jobs:
            print("Empty queue")
            return
        
        print("Current jobs in queue:")
        for i, job in enumerate(self.jobs, 1):
            print(f"  {i}. {job.id} - Priority {job.priority} - {job.material}")
    def get_queue_size(self):
        
        return len(self.jobs)

if __name__ == "__main__":

    
    queue = JobQueue()

    job1 = Job("JOB1", "Plastic 1", 60, 1)
    job2 = Job("JOBB2", "Plastic 2", 20, 1) 
    job3 = Job("JOBB3", "Plastic 2", 45, 3)

    queue.add_job(job1)
    queue.add_job(job2)
    queue.add_job(job3)

    print(f"\n Queue size: {queue.get_queue_size()}")

    
    print("\n--- Arrival order ---")
    queue.list_jobs()

    
    queue.sort_by_priority()

    
    print("\n--- Priority order ---")
    queue.list_jobs()


    print("\n--- Processing jobs ---")
    while queue.get_queue_size() > 0:
        next_job = queue.get_next_job()
        print(f"Processing: {next_job}")


