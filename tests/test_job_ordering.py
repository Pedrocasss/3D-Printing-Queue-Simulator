import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from simulator import PrinterSimulator
from models import Job

def test_priority_order():
    sim = PrinterSimulator(num_printers=1, time_scale=0.01)
    
    sim.add_job(Job("J1", "PLA", 2, 1))    # priority 1
    sim.add_job(Job("J2", "ABS", 1, 2))    # priority 2
    sim.add_job(Job("J3", "PETG", 3, 1))   # priority 1
    
    for job in sim.job_queue.jobs:
        print(f"  {job.id}: priority {job.priority}, created_at {job.created_at}")
    
    sim.run_until_complete()
    
    report = sim.get_report()
    order = [j['id'] for j in report['jobs'] if j['status'] == "completed"]
    print(f"Order of completion: {order}")
    
    assert order == ["J1", "J3", "J2"]