def chunk_text(text, chunk_size=1000, overlap=200):
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks

if __name__ == "__main__":
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