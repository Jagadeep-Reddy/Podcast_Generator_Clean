from .base_agent import BaseAgent
from prompts import PROMPT_SCRIPT_WRITER_V1

class ScriptWriterAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("ScriptWriterAgent", llm_client)

    def execute(self, context):
        self.log("Drafting the podcast script...")
        topic = context.get('topic')
        plan = context.get('plan')
        retrieved_context = context.get('retrieved_context')
        voice = context.get('voice', 'casual')

        prompt = PROMPT_SCRIPT_WRITER_V1.format(
            voice=voice,
            topic=topic,
            plan=plan,
            retrieved_context=retrieved_context[:3000]
        )
        
        script = self.llm_client.complete(prompt)
        context['script'] = script
        self.log("Script drafted.")
        return context
