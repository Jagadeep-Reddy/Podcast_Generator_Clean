import threading
import time
import uuid
import json
import os
import logging
from datetime import datetime
from agents.planning_agent import PlanningAgent
from agents.retrieval_agent import RetrievalAgent
from agents.script_writer_agent import ScriptWriterAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.tts_agent import TTSAgent
from agents.audio_mixer_agent import AudioMixerAgent
from llm_client import SimpleLLMClient

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    def __init__(self, output_folder):
        self.llm_client = SimpleLLMClient()
        self.output_folder = output_folder
        self.jobs = {} # job_id -> {status, progress, result, error}
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Initialize Agents
        self.agents = [
            PlanningAgent(self.llm_client),
            RetrievalAgent(self.llm_client),
            ScriptWriterAgent(self.llm_client),
            FactCheckerAgent(self.llm_client),
            TTSAgent(self.llm_client, output_folder),
            AudioMixerAgent(self.llm_client)
        ]

    def start_job(self, context):
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            'status': 'running',
            'current_step': 'Initializing',
            'steps_completed': [],
            'context': context,
            'result': None,
            'error': None
        }
        
        # Run in background thread
        thread = threading.Thread(target=self._run_workflow, args=(job_id,))
        thread.start()
        
        return job_id

    def _run_workflow(self, job_id):
        job = self.jobs[job_id]
        context = job['context']
        
        try:
            for agent in self.agents:
                step_name = agent.name
                job['current_step'] = step_name
                
                # Execute Agent
                print(f"[{job_id}] Starting {step_name}")
                context = agent.execute(context)
                
                # Update Progress
                job['steps_completed'].append(step_name)
                job['context'] = context # Update context with new data
                
                # Simulate a small delay for visualization
                time.sleep(1) 
            
            job['status'] = 'completed'
            job['result'] = {
                'script': context.get('script'),
                'audio_url': context.get('final_audio_url'),
                'plan': context.get('plan'),
                'verification': context.get('verification_notes')
            }
            logger.info(f"[{job_id}] Workflow completed successfully.")
            
            # Save Run History
            run_log_path = os.path.join(self.logs_dir, f"run_{job_id}.json")
            with open(run_log_path, 'w') as f:
                json.dump(job, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"[{job_id}] Workflow failed: {e}")
            job['status'] = 'failed'
            job['error'] = str(e)
            
            # Save Failed Run History
            run_log_path = os.path.join(self.logs_dir, f"run_{job_id}_failed.json")
            with open(run_log_path, 'w') as f:
                json.dump(job, f, indent=2, default=str)

    def get_job_status(self, job_id):
        return self.jobs.get(job_id)
