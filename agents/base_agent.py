from abc import ABC, abstractmethod
import time

class BaseAgent(ABC):
    def __init__(self, name, llm_client):
        self.name = name
        self.llm_client = llm_client

    @abstractmethod
    def execute(self, context):
        """
        Execute the agent's task.
        :param context: A dictionary containing the current state/data of the workflow.
        :return: Updated context or specific output.
        """
        pass

    def log(self, message):
        print(f"[{self.name}] {message}")
