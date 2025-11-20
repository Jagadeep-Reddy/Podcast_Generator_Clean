import networkx as nx
from entity_extractor import EntityExtractor
from llm_client import SimpleLLMClient

class Entity:
    def __init__(self, name, type, description, source_chunks=None):
        self.name = name
        self.type = type
        self.description = description
        self.source_chunks = source_chunks if source_chunks else set()

class Relationship:
    def __init__(self, source, target, description, weight=1):
        self.source = source
        self.target = target
        self.description = description
        self.weight = weight

class KnowledgeGraph:
    def __init__(self):
        self.entities = {}
        self.relationships = []

    def add_entity(self, name, type, description, chunk_id):
        if name in self.entities:
            self.entities[name].source_chunks.add(chunk_id)
            if description not in self.entities[name].description:
                self.entities[name].description += " " + description
        else:
            self.entities[name] = Entity(name, type, description, {chunk_id})

    def add_relationship(self, source, target, description):
        for rel in self.relationships:
            if rel.source == source and rel.target == target:
                rel.weight += 1
                return

        self.relationships.append(Relationship(source, target, description))

    def get_neighbors(self, entity_name):
        neighbors = set()
        for rel in self.relationships:
            if rel.source == entity_name:
                neighbors.add(rel.target)
            elif rel.target == entity_name:
                neighbors.add(rel.source)
        return neighbors

    def get_subgraph(self, entity_names, depth=1):
        all_entities = set(entity_names)
        queue = [(name, 0) for name in entity_names]
        visited = set(entity_names)

        while queue:
            entity, dist = queue.pop(0)
            if dist >= depth:
                continue

            for neighbor in self.get_neighbors(entity):
                if neighbor not in visited:
                    visited.add(neighbor)
                    all_entities.add(neighbor)
                    queue.append((neighbor, dist + 1))

        subgraph = KnowledgeGraph()
        for name in all_entities:
            if name in self.entities:
                e = self.entities[name]
                for chunk_id in e.source_chunks:
                    subgraph.add_entity(e.name, e.type, e.description, chunk_id)

        for rel in self.relationships:
            if rel.source in all_entities and rel.target in all_entities:
                subgraph.add_relationship(rel.source, rel.target, rel.description)

        return subgraph

    def to_networkx(self):
        G = nx.Graph()
        for name in self.entities:
            G.add_node(name)
        for rel in self.relationships:
            G.add_edge(rel.source, rel.target, weight=rel.weight)
        return G

    def stats(self):
        return {
            "num_entities": len(self.entities),
            "num_relationships": len(self.relationships),
            "avg_degree": 2 * len(self.relationships) / len(self.entities) if self.entities else 0
        }

if __name__ == "__main__":
    import matplotlib.pyplot as plt

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

    G = graph.to_networkx()
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue',
            node_size=3000, font_size=10, font_weight='bold')
    plt.title("Knowledge Graph Visualization")
    plt.tight_layout()
    plt.show()

    print("Graph visualized above!")