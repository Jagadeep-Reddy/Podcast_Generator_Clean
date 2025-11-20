import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import community
from graph_models import KnowledgeGraph
from entity_extractor import EntityExtractor
from llm_client import SimpleLLMClient

class CommunityDetector:
    def detect_communities(self, graph):
        G = graph.to_networkx()

        if len(G.nodes()) == 0:
            return {}

        communities_list = community.louvain_communities(G, seed=42)

        communities_dict = {}
        for idx, comm in enumerate(communities_list):
            communities_dict[idx] = list(comm)

        return communities_dict

if __name__ == "__main__":
    client = SimpleLLMClient()
    extractor = EntityExtractor(client)
    graph_large = KnowledgeGraph()

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

    detector = CommunityDetector()
    communities = detector.detect_communities(graph_large)

    print(f"Found {len(communities)} communities\n")
    for comm_id, entities in communities.items():
        print(f"Community {comm_id}: {entities}")

    G = graph_large.to_networkx()
    pos = nx.spring_layout(G, seed=42)

    colors = []
    for node in G.nodes():
        for comm_id, entities in communities.items():
            if node in entities:
                colors.append(comm_id)
                break

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color=colors,
            cmap='Set3', node_size=3000, font_size=9)
    plt.title("Communities (colors = different communities)")
    plt.tight_layout()
    plt.show()

    print("Communities visualization complete!")