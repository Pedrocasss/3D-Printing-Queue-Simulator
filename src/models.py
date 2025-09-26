import time

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


if __name__ == "__main__":

    job1 = Job("My first job", "Plastic", 120, 1)
    print(f"Job created: {job1.id}")
    print(f"Initial status: {job1.status}")
    job1.start_printing()
    
    time.sleep(2)
    job1.complete_printing()

    print(f"Waiting time: {job1.get_wait_time():.2f}s")
    print(f"exec time: {job1.get_run_time():.2f}s")