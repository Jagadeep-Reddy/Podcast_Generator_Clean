from .base_agent import BaseAgent
from prompts import PROMPT_PLANNING_V1

class PlanningAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("PlanningAgent", llm_client)

    def execute(self, context):
        self.log("Analyzing request and creating a podcast plan...")
        topic = context.get('topic')
        source_preview = context.get('source_content', '')[:1000]

        prompt = PROMPT_PLANNING_V1.format(topic=topic, source_preview=source_preview)
        
        plan = self.llm_client.complete(prompt)
        context['plan'] = plan
        self.log("Plan created.")
        return context
