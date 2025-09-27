import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from simulator import PrinterSimulator
from models import Job

def test_all_together():
    sim = PrinterSimulator(num_printers=1, time_scale=0.01)
    

    jobs = [
        Job("high1", "PLA", 1, 1),
        Job("low", "ABS", 1, 3), 
        Job("high2", "PETG", 1, 1),
        Job("medium", "PLA", 1, 2)
    ]
    
    for job in jobs:
        sim.add_job(job)
    
    assert len(sim.all_jobs) == 4
    
    sim.run_until_complete()
    
    report = sim.get_report()
    completed = [j for j in report['jobs'] if j['status'] == "completed"]
    order = [j['id'] for j in completed]
    
    assert order == ["high1", "high2", "medium", "low"]
    
    assert len(completed) == 4
    for job in completed:
        assert job['wait_time'] >= 0
        assert job['run_time'] > 0