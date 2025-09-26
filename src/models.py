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

if __name__ == "__main__":

    job1 = Job("My first job", "Plastic", 120, 1)
    print(f"Job created: {job1.id}")
    print(f"Initial status: {job1.status}")
    job1.start_printing()
    print(f"Status after starting: {job1.status}")