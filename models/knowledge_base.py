import chromadb
from sentence_transformers import SentenceTransformer

class KnowledgeBase:
    def __init__(self, db_path="./data/embeddings/chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("ayurvedic_knowledge")
        self.encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def add_documents(self, chunks):
        docs, metas, ids = [], [], []
        for i, c in enumerate(chunks):
            docs.append(c['text'])
            metas.append({'source': c['source'], 'topic': c['topic'], 'chunk_id': c['chunk_id']})
            ids.append(f"doc_{i}")
        self.collection.add(documents=docs, metadatas=metas, ids=ids)
        print(f"Added {len(docs)} docs.")

    def search_relevant_context(self, query, n_results=5):
        results = self.collection.query(query_texts=[query], n_results=n_results)
        context = []
        for i in range(len(results['documents'][0])):
            context.append({'text': results['documents'][0][i], 'meta': results['metadatas'][0][i]})
        return context
