import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from simulator import PrinterSimulator
from models import Job

def test_final_report():

    sim = PrinterSimulator(num_printers=1, time_scale=0.01)
    
    sim.add_job(Job("test-job", "PLA", 1, 1))
    sim.run_until_complete()
    
    report = sim.get_report()
    
    
    assert 'jobs' in report
    assert 'metrics' in report
    assert len(report['jobs']) == 1
    
    job = report['jobs'][0]
    assert job['id'] == "test-job"
    assert job['status'] == "completed"
    assert job['wait_time'] is not None
    assert job['run_time'] is not None