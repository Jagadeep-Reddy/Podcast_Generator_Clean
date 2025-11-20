import numpy as np
from llm_client import SimpleLLMClient
from text_utils import chunk_text
from entity_extractor import EntityExtractor
from graph_models import KnowledgeGraph
from community_detector import CommunityDetector
from community_summarizer import CommunitySummarizer
from query_engine import QueryEngine
from graph_rag import SimpleGraphRAG

def test_text_chunking():
    print("="*60)
    print("TESTING TEXT CHUNKING")
    print("="*60)

    test_text = """
    Apple Inc. is an American multinational technology company.
    It was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
    Steve Jobs served as CEO until 2011.
    The company is headquartered in Cupertino, California.
    Apple is known for products like the iPhone, iPad, and Mac computers.
    """ * 10

    chunks = chunk_text(test_text, chunk_size=200, overlap=50)
    print(f"Created {len(chunks)} chunks")
    print(f"First chunk: {chunks[0][:100]}...")
    print(f"Last chunk: {chunks[-1][:100]}...")

def test_llm_client():
    print("\n" + "="*60)
    print("TESTING LLM CLIENT")
    print("="*60)

    client = SimpleLLMClient()

    response = client.complete("What is 2+2?")
    print("Completion:", response)

    embedding = client.embed("Apple Inc.")
    print(f"Embedding shape: {embedding.shape}")
    print(f"First 5 values: {embedding[:5]}")

    emb1 = client.embed("Apple Inc. makes iPhones")
    emb2 = client.embed("Apple produces smartphones")
    emb3 = client.embed("Bananas are yellow fruit")

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    print(f"Similarity 1-2: {cosine_similarity(emb1, emb2):.3f}")
    print(f"Similarity 1-3: {cosine_similarity(emb1, emb3):.3f}")

def test_entity_extraction():
    print("\n" + "="*60)
    print("TESTING ENTITY EXTRACTION")
    print("="*60)

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

def test_knowledge_graph():
    print("\n" + "="*60)
    print("TESTING KNOWLEDGE GRAPH")
    print("="*60)

    client = SimpleLLMClient()
    extractor = EntityExtractor(client)
    graph = KnowledgeGraph()

    texts = [
        "Apple Inc. was founded by Steve Jobs in 1976.",
        "Steve Jobs was the CEO of Apple until 2011.",
        "Apple is headquartered in Cupertino, California."
    ]

    for i, text in enumerate(texts):
        result = extractor.extract(text)

        for entity in result['entities']:
            graph.add_entity(entity['name'], entity['type'], entity['description'], i)

        for rel in result['relationships']:
            graph.add_relationship(rel['source'], rel['target'], rel['description'])

    print("Graph stats:", graph.stats())
    print("\nEntities:")
    for name, entity in graph.entities.items():
        print(f"  {name} ({entity.type})")

    print("\nRelationships:")
    for rel in graph.relationships:
        print(f"  {rel.source} → {rel.target} (weight: {rel.weight})")

    print("\nNeighbors of Apple:", graph.get_neighbors("Apple"))

def test_community_detection():
    print("\n" + "="*60)
    print("TESTING COMMUNITY DETECTION")
    print("="*60)

    client = SimpleLLMClient()
    extractor = EntityExtractor(client)
    graph_large = KnowledgeGraph()
    detector = CommunityDetector()

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

    print(f"Found {len(communities)} communities\n")
    for comm_id, entities in communities.items():
        print(f"Community {comm_id}: {entities}")

def test_community_summarization():
    print("\n" + "="*60)
    print("TESTING COMMUNITY SUMMARIZATION")
    print("="*60)

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

def test_query_engine():
    print("\n" + "="*60)
    print("TESTING QUERY ENGINE")
    print("="*60)

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

def test_complete_graphrag():
    print("\n" + "="*60)
    print("TESTING COMPLETE GRAPHRAG SYSTEM")
    print("="*60)

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

if __name__ == "__main__":
    print("✅ Setup complete!")
    print("🚀 Running comprehensive GraphRAG tests...\n")

    test_text_chunking()
    test_llm_client()
    test_entity_extraction()
    test_knowledge_graph()
    test_community_detection()
    test_community_summarization()
    test_query_engine()
    test_complete_graphrag()

    print("\n🎉 All tests completed successfully!")