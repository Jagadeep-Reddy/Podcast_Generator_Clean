from .base_agent import BaseAgent
from prompts import PROMPT_FACT_CHECKER_V1

class FactCheckerAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__("FactCheckerAgent", llm_client)

    def execute(self, context):
        self.log("Verifying facts in the script...")
        script = context.get('script')
        source_content = context.get('source_content')

        prompt = PROMPT_FACT_CHECKER_V1.format(
            script=script[:2000],
            source_content=source_content[:1000]
        )
        
        verification = self.llm_client.complete(prompt)
        context['verification_notes'] = verification
        self.log(f"Fact check complete: {verification[:50]}...")
        return context
