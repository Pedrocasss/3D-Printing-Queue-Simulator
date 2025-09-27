import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from simulator import PrinterSimulator
from models import Job

def test_enqueueing():
    sim = PrinterSimulator(num_printers=1, time_scale=0.01)

    sim.add_job(Job("J1", "PLA", 2, 1))
    sim.add_job(Job("J2", "ABS", 1, 2))

    assert len(sim.all_jobs) == 2
    assert sim.job_queue.get_queue_size() == 2