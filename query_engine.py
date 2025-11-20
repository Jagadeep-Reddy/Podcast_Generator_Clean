import numpy as np
from llm_client import SimpleLLMClient
from graph_models import KnowledgeGraph
from entity_extractor import EntityExtractor
from community_detector import CommunityDetector
from community_summarizer import CommunitySummarizer

LOCAL_QUERY_PROMPT = """
Use this knowledge graph to answer the question.

Entities:
{entities}

Relationships:
{relationships}

Question: {question}

Answer based only on the provided information.

Answer:
"""

GLOBAL_QUERY_PROMPT = """
Use these community summaries to answer the question.

{summaries}

Question: {question}

Provide a comprehensive answer synthesizing the summaries.

Answer:
"""

class QueryEngine:
    def __init__(self, llm_client, graph, communities, community_summaries):
        self.llm_client = llm_client
        self.graph = graph
        self.communities = communities
        self.community_summaries = community_summaries

    def local_search(self, question, top_k=5):
        question_emb = self.llm_client.embed(question)
        relevant_entities = self.find_relevant_entities(question_emb, top_k)

        subgraph = self.graph.get_subgraph(relevant_entities, depth=2)

        entity_text = self.format_entities(subgraph.entities)
        rel_text = self.format_relationships(subgraph.relationships)

        prompt = LOCAL_QUERY_PROMPT.format(
            entities=entity_text,
            relationships=rel_text,
            question=question
        )

        return self.llm_client.complete(prompt)

    def global_search(self, question, top_k=3):
        question_emb = self.llm_client.embed(question)
        relevant_comms = self.find_relevant_communities(question_emb, top_k)
        summaries_text = self.format_summaries(relevant_comms)

        prompt = GLOBAL_QUERY_PROMPT.format(
            summaries=summaries_text,
            question=question
        )

        return self.llm_client.complete(prompt)

    def find_relevant_entities(self, query_emb, top_k):
        names = list(self.graph.entities.keys())
        descriptions = [self.graph.entities[n].description for n in names]

        embs = self.llm_client.embed_batch(descriptions)

        sims = np.dot(embs, query_emb) / (
            np.linalg.norm(embs, axis=1) * np.linalg.norm(query_emb)
        )

        top_indices = np.argsort(sims)[-top_k:][::-1]
        return [names[i] for i in top_indices]

    def find_relevant_communities(self, query_emb, top_k):
        comm_ids = list(self.community_summaries.keys())
        summaries = [self.community_summaries[i] for i in comm_ids]

        embs = self.llm_client.embed_batch(summaries)

        sims = np.dot(embs, query_emb) / (
            np.linalg.norm(embs, axis=1) * np.linalg.norm(query_emb)
        )

        top_indices = np.argsort(sims)[-top_k:][::-1]
        return [comm_ids[i] for i in top_indices]

    def format_entities(self, entities):
        return "\n".join([
            f"- {name} ({e.type}): {e.description}"
            for name, e in entities.items()
        ])

    def format_relationships(self, relationships):
        return "\n".join([
            f"- {r.source} → {r.target}: {r.description}"
            for r in relationships
        ])
    
    def format_summaries(self, relevant_comms):
        summaries_text = "\n\n".join([
            f"Community {i}:\n{self.community_summaries[i]}"
            for i in relevant_comms
        ])
        return summaries_text

if __name__ == "__main__":
    client = SimpleLLMClient()
    extractor = EntityExtractor(client)
    comprehensive_graph = KnowledgeGraph()
    detector = CommunityDetector()
    summarizer = CommunitySummarizer(client)

    texts_comprehensive = [
        "Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.",
        "Steve Jobs served as CEO of Apple from 1997 to 2011.",
        "Apple is headquartered in Cupertino, California.",
        "The iPhone was introduced by Apple in 2007.",
        "Steve Wozniak designed the Apple I computer."
    ]

    for i, text in enumerate(texts_comprehensive):
        result = extractor.extract(text)
        for entity in result['entities']:
            comprehensive_graph.add_entity(entity['name'], entity['type'], entity['description'], i)
        for rel in result['relationships']:
            comprehensive_graph.add_relationship(rel['source'], rel['target'], rel['description'])

    comprehensive_communities = detector.detect_communities(comprehensive_graph)
    comprehensive_summaries = {}
    for comm_id, entities in comprehensive_communities.items():
        subgraph = comprehensive_graph.get_subgraph(entities)
        comprehensive_summaries[comm_id] = summarizer.summarize_community(subgraph)

    query_engine = QueryEngine(client, comprehensive_graph, comprehensive_communities, comprehensive_summaries)

    print("Query engine initialized successfully!")

    print("LOCAL SEARCH")
    print("="*60)

    question = "Who founded Apple?"
    answer = query_engine.local_search(question, top_k=3)
    print(f"Q: {question}")
    print(f"A: {answer}\n")

    question = "What is the relationship between Steve Jobs and Apple?"
    answer = query_engine.local_search(question, top_k=3)
    print(f"Q: {question}")
    print(f"A: {answer}\n")

    print("\nGLOBAL SEARCH")
    print("="*60)

    question = "What are the main topics in this corpus?"
    answer = query_engine.global_search(question, top_k=2)
    print(f"Q: {question}")
    print(f"A: {answer}\n")