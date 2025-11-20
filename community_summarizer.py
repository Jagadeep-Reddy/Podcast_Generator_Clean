from llm_client import SimpleLLMClient
from graph_models import KnowledgeGraph
from entity_extractor import EntityExtractor
from community_detector import CommunityDetector

COMMUNITY_SUMMARY_PROMPT = """
Analyze this community of related entities from a knowledge graph.

Entities:
{entities}

Relationships:
{relationships}

Write a summary (200-300 words) that:
1. Identifies the main theme of this community
2. Explains how entities are related
3. Highlights key insights

Summary:
"""

class CommunitySummarizer:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def summarize_community(self, community_graph):
        entity_lines = []
        for name, entity in community_graph.entities.items():
            entity_lines.append(f"- {name} ({entity.type}): {entity.description}")
        entity_text = "\n".join(entity_lines)

        rel_lines = []
        for rel in community_graph.relationships:
            rel_lines.append(f"- {rel.source} → {rel.target}: {rel.description}")
        rel_text = "\n".join(rel_lines)

        prompt = COMMUNITY_SUMMARY_PROMPT.format(
            entities=entity_text,
            relationships=rel_text
        )

        return self.llm_client.complete(prompt)

if __name__ == "__main__":
    client = SimpleLLMClient()
    extractor = EntityExtractor(client)
    graph_large = KnowledgeGraph()
    detector = CommunityDetector()
    summarizer = CommunitySummarizer(client)

    texts_large = [
        "Apple Inc. was founded by Steve Jobs in Cupertino.",
        "Steve Jobs also founded Pixar Animation Studios.",
        "Pixar is now owned by Disney.",
        "Michael Jordan played for the Chicago Bulls.",
        "The Chicago Bulls won six NBA championships.",
        "Phil Jackson coached the Chicago Bulls."
    ]

    for i, text in enumerate(texts_large):
        result = extractor.extract(text)
        for entity in result['entities']:
            graph_large.add_entity(entity['name'], entity['type'], entity['description'], i)
        for rel in result['relationships']:
            graph_large.add_relationship(rel['source'], rel['target'], rel['description'])

    communities = detector.detect_communities(graph_large)

    for comm_id, entity_names in communities.items():
        print(f"\n{'='*60}")
        print(f"COMMUNITY {comm_id}")
        print(f"Entities: {entity_names}")
        print(f"{'='*60}")

        community_subgraph = graph_large.get_subgraph(entity_names)
        summary = summarizer.summarize_community(community_subgraph)
        print(f"\nSummary:\n{summary}")