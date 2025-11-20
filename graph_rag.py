import matplotlib.pyplot as plt
import networkx as nx
from llm_client import SimpleLLMClient
from text_utils import chunk_text
from entity_extractor import EntityExtractor
from graph_models import KnowledgeGraph
from community_detector import CommunityDetector
from community_summarizer import CommunitySummarizer
from query_engine import QueryEngine
plt.ion()

class SimpleGraphRAG:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.extractor = EntityExtractor(llm_client)
        self.graph = KnowledgeGraph()
        self.detector = CommunityDetector()
        self.summarizer = CommunitySummarizer(llm_client)
        self.communities = {}
        self.community_summaries = {}
        self.query_engine = None

    def insert(self, documents, chunk_size=1000):
        print("📄 Chunking documents...")
        all_chunks = []
        for doc in documents:
            chunks = chunk_text(doc, chunk_size)
            all_chunks.extend(chunks)
        print(f"   Created {len(all_chunks)} chunks")

        print("\n🔍 Extracting entities and relationships...")
        for i, chunk in enumerate(all_chunks):
            result = self.extractor.extract(chunk)

            for entity in result['entities']:
                self.graph.add_entity( entity['name'], entity['type'], entity['description'], i)

            for rel in result['relationships']:
                self.graph.add_relationship( rel['source'], rel['target'], rel['description'])

            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{len(all_chunks)} chunks")

        stats = self.graph.stats()
        print(f"   Graph: {stats['num_entities']} entities, "
              f"{stats['num_relationships']} relationships")

        print("\n🌐 Detecting communities...")
        self.communities = self.detector.detect_communities(self.graph)
        print(f"   Found {len(self.communities)} communities")

        print("\n📝 Summarizing communities...")
        for comm_id, entities in self.communities.items():
            subgraph = self.graph.get_subgraph(entities)
            self.community_summaries[comm_id] = self.summarizer.summarize_community(subgraph)

        print("\n🚀 Initializing query engine...")
        self.query_engine = QueryEngine(
            self.llm_client,
            self.graph,
            self.communities,
            self.community_summaries
        )

        print("\n✅ GraphRAG ready!")

    def query_local(self, question, top_k=5):
        if not self.query_engine:
            raise ValueError("Must call insert() first")
        return self.query_engine.local_search(question, top_k)

    def query_global(self, question, top_k=3):
        if not self.query_engine:
            raise ValueError("Must call insert() first")
        return self.query_engine.global_search(question, top_k)

    def visualize_graph(self):
        G = self.graph.to_networkx()
        pos = nx.spring_layout(G, seed=42)

        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue',
                node_size=3000, font_size=8, font_weight='bold')
        plt.title("Complete Knowledge Graph")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    client = SimpleLLMClient()
    graphrag = SimpleGraphRAG(client)

    documents = [
        """
        Apple Inc. is an American multinational technology company headquartered in
        Cupertino, California. It was founded by Steve Jobs, Steve Wozniak, and
        Ronald Wayne in 1976. Steve Jobs served as CEO until 2011.
        """,
        """
        The iPhone is a line of smartphones produced by Apple Inc. It was first
        introduced in 2007 by Steve Jobs. The iPhone revolutionized the smartphone
        industry with its touchscreen interface.
        """,
        """
        Steve Wozniak, also known as "Woz", is a computer engineer who co-founded
        Apple Computer with Steve Jobs. He designed the Apple I and Apple II computers
        in the late 1970s.
        """
    ]

    graphrag.insert(documents, chunk_size=500)
    graphrag.visualize_graph()

    print("\n" + "="*70)
    print("QUERYING THE COMPLETE GRAPHRAG SYSTEM")
    print("="*70)

    questions = [
        "Who founded Apple?",
        "What is the relationship between Steve Jobs and the iPhone?",
        "What are the main topics discussed in these documents?"
    ]

    for q in questions:
        print(f"\n🔍 Question: {q}")
        print(f"📍 Local Search: {graphrag.query_local(q)}")
        print(f"🌍 Global Search: {graphrag.query_global(q)}")
        print("-" * 50)