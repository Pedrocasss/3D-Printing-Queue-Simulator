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

    sim.run_until_complete()

    report = sim.get_report()
    started_order = sorted(
        [j for j in report['jobs'] if j['status'] == "completed"],
        key=lambda x: x['started_at']
    )
    order = [j['id'] for j in started_order]

    print(f"Order of START: {order}")
    assert order == ["J1", "J3", "J2"]
