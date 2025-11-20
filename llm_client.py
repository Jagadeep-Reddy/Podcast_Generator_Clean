import os
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

class SimpleLLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        print(f"DEBUG: LLMClient loaded key: {api_key[:5]}...{api_key[-4:] if len(api_key)>10 else ''} (Len: {len(api_key)})")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    # @traceable(run_type="llm")
    def complete(self, prompt, system_prompt=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content

    def embed(self, text):
        embedding = self.embedding_model.encode(text)
        return np.array(embedding)

    def embed_batch(self, texts):
        embeddings = self.embedding_model.encode(texts)
        return np.array(embeddings)

if __name__ == "__main__":
    print("✅ Setup complete!")

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