import json
import re
from llm_client import SimpleLLMClient

EXTRACTION_PROMPT = """
Extract entities and relationships from this text.

Entity Types: Person, Organization, Location, Event, Concept

For each entity provide:
- name: exact name from text
- type: one of the entity types above
- description: brief description (1-2 sentences)

For each relationship provide:
- source: entity name
- target: entity name
- description: nature of relationship (1 sentence)

Text:
{text}

Return only valid JSON in this format:
{{
  "entities": [
    {{"name": "Apple", "type": "Organization", "description": "Technology company"}}
  ],
  "relationships": [
    {{"source": "Steve Jobs", "target": "Apple", "description": "Founded the company"}}
  ]
}}
"""

class EntityExtractor:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def extract(self, text):
        prompt = EXTRACTION_PROMPT.format(text=text)
        response = self.llm_client.complete(prompt)

        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            return {"entities": [], "relationships": []}

if __name__ == "__main__":
    client = SimpleLLMClient()
    extractor = EntityExtractor(client)

    test_text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976
    in Cupertino, California. Steve Jobs served as CEO until 2011.
    """

    result = extractor.extract(test_text)

    print("ENTITIES:")
    for entity in result['entities']:
        print(f"  - {entity['name']} ({entity['type']}): {entity['description']}")

    print("\nRELATIONSHIPS:")
    for rel in result['relationships']:
        print(f"  - {rel['source']} → {rel['target']}: {rel['description']}")