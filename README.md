# 3D Printer Queue Simulator

A threaded simulation system that manages multiple 3D printers processing a priority-based job queue. Built with Python, featuring comprehensive CLI interfaces and detailed reporting capabilities.

## Features

### Core Functionality (MUST Requirements)

1. Job model with fields: id, material, est_time (seconds), priority (integer), created_at
2. A queue structure that processes jobs by priority (higher priority first — define and document whether a lower or higher number is "more urgent")
3. Simulate processing of the jobs by N printers (configurable)
4. Handle concurrency/state safely — for example using locks, asyncio, or a thread-safe priority queue
5. Output a final report (JSON or CSV) with the status of each job: queued, running, completed, cancelled and timestamps: started_at, finished_at
6. Provide instructions in the README and usage examples
7. Basic unit tests (pytest) covering enqueueing, job ordering and final report

### Advanced Features (SHOULD Requirements)

1. Simple CLI to: add jobs, list queue, cancel jobs
2. Metrics report: average waiting time, throughput, total printer occupancy time
3. Simulation with a time scaling factor (for example time_scale) so you do not have to wait real seconds

## Project Structure

```
printer-simulator/
├── src/
│   ├── models.py           # Job and Printer data models
│   ├── queue_manager.py    # Thread-safe priority queue implementation
│   └── simulator.py        # Main simulation engine
├── tests/
│   ├── test_all.py         # Comprehensive integration tests
│   ├── test_enqueueing.py  # Job queue tests
│   ├── test_final_report.py # Report generation tests
│   └── test_job_ordering.py # Priority ordering tests
├── cli.py                  # Simple CLI (independent commands)
├── cli_interactive.py      # Advanced interactive CLI
├── requirements.txt        # Python dependencies
└── README.md
```

## Installation

### Requirements
- Python 3.7+
- No external dependencies required (uses only standard library)

### Setup
```bash
git clone <repository-url>
cd printer-simulator
```

## Usage

### Simple CLI (Independent Commands)

The basic CLI follows the PDF requirements with independent commands:

```bash
# Add jobs to queue
python cli.py add --id job1 --material PLA --time 120 --priority 1
python cli.py add --id job2 --material ABS --time 180 --priority 2

# List current queue
python cli.py list

# Cancel a job
python cli.py cancel job1

# Run simulation and generate reports
python cli.py run

# Load jobs from file
python cli.py load sample_jobs.json

# Clear all jobs
python cli.py clear
```

#### Configuration Options
```bash
# Set number of printers and time scale
python cli.py --printers 3 --time-scale 0.01 add --id job1 --material PLA --time 60 --priority 1
python cli.py --printers 3 --time-scale 0.01 run
```

### Interactive CLI (Advanced Features)

For enhanced user experience and real-time configuration:

```bash
python cli_interactive.py interactive
```

Interactive commands:
- `add` - Add jobs with guided input
- `list` - Show queue status and active jobs
- `config` - Reconfigure printers and time scale
- `status` - Display current system configuration
- `run` - Execute simulation
- `report` - Show detailed metrics
- `help` - Command reference

## Priority System

Jobs are processed by priority value where **lower numbers indicate higher priority**:
- Lower priority values are processed first
- Higher priority values are processed last
- Within the same priority level, jobs follow FIFO (First-In-First-Out) ordering based on creation time

Example: Priority 1 jobs execute before Priority 2 jobs, which execute before Priority 3 jobs.

## Time Scaling

The `time_scale` parameter controls simulation speed:
- `1.0` - Real time (1 second job = 1 second simulation)
- `0.01` - Fast simulation (1 second job = 0.01 seconds simulation)
- `100.0` - Slow simulation (1 second job = 100 seconds simulation)

Recommended values:
- Testing: `0.01` (very fast)
- Demonstration: `0.1` (fast but observable)
- Real-time simulation: `1.0`

## Report Generation

Simulation reports include:

### Job Details
- Job status (queued, started, completed, cancelled)
- Timestamps (created_at, started_at, completed_at)
- Wait time and run time (both real and scaled)
- Material and priority information

### Performance Metrics
- Average wait time and median wait time
- Throughput (total jobs / total simulation time)
- Printer utilization (busy_time / total simulation time per printer)
- Total simulation duration and job statistics

### Output Formats
- **JSON**: Complete structured data (`simulation_report_<timestamp>.json`)
- **CSV**: Tabular job data (`simulation_report_<timestamp>.csv`)

## Sample Job File Format

```json
[
  {
    "id": "urgent_print_1",
    "material": "PLA",
    "est_time": 120,
    "priority": 1
  },
  {
    "id": "normal_print_1", 
    "material": "ABS",
    "est_time": 180,
    "priority": 2
  }
]
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_job_ordering.py -v
python -m pytest tests/test_final_report.py -v
```

Test coverage includes:
- Job enqueueing and priority ordering
- Multi-printer concurrent processing
- Report generation and metrics calculation
- Job cancellation functionality

## Architecture

### Thread Safety
The system uses `threading.Lock` for safe concurrent access to shared state:
- Job queue operations
- Printer status updates
- Report generation

### Simulation Engine
- **PrinterSimulator**: Main coordination class
- **JobQueue**: Thread-safe priority queue with FIFO ordering
- **Job/Printer Models**: Data structures with lifecycle management

### Worker Threads
Each printer runs in a dedicated daemon thread:
- Continuously polls for available jobs
- Processes jobs according to priority
- Updates metrics and job status
- Handles graceful shutdown

## Examples

### Basic Workflow
```bash
# Setup jobs
python cli.py add --id print1 --material PLA --time 60 --priority 1
python cli.py add --id print2 --material ABS --time 120 --priority 2
python cli.py add --id print3 --material PETG --time 90 --priority 1

# Check queue (priority 1 jobs will be first)
python cli.py list

# Run with 2 printers, fast simulation
python cli.py --printers 2 --time-scale 0.01 run
```

### Performance Testing
```bash
# Load multiple jobs and test throughput
python cli.py load jobs_batch.json
python cli.py --printers 5 --time-scale 0.005 run
```

## Next Steps (OPTIONAL/BONUS Features)

1. Dynamic priority (increase priority of jobs waiting too long)
2. Preemption: a higher-priority job interrupts a running job
3. Simple persistence (SQLite) for job history
4. REST API (FastAPI) to create/list/cancel jobs
5. Visualization (e.g. with matplotlib) of printer utilization or a Gantt chart

## Architecture
- **Priority Definition**: Lower numbers indicate higher priority (inverse numerical order)
- **Concurrency**: I chose threading with locks for simplicity and small-scale deployments. For high-scale production systems, I would recommend async/await with asyncio or message queue systems like Celery/Redis for better scalability
- **Time Scaling**: Applied to job execution time for flexible testing speeds
- **State Persistence**: CLI commands use file-based state sharing for independence