"""
ChromaDB manager for vector storage and retrieval.
Manages local chromadb collection with metadata support.
"""
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from src.config import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME


class ChromaDBManager:
    """Interface to ChromaDB for vector storage."""

    def __init__(self, db_path: str = CHROMA_DB_PATH, collection_name: str = CHROMA_COLLECTION_NAME):
        """
        Initialize ChromaDB client.
        
        Args:
            db_path: Path to store ChromaDB data
            collection_name: Name of the collection to use
        """
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        
        # Get or create collection with metadata index
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[Dict]) -> List[str]:
        """
        Add documents/chunks to ChromaDB.
        
        Args:
            documents: List of dicts with 'id', 'embedding', 'text', 'metadata'
                      Example: {
                          'id': 'chunk_1',
                          'embedding': [0.1, 0.2, ...],
                          'text': 'document text',
                          'metadata': {'page': 1, 'modality': 'text'}
                      }
            
        Returns:
            List of added document IDs
        """
        if not documents:
            return []
        
        ids = []
        embeddings = []
        documents_list = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc['id'])
            embeddings.append(doc['embedding'])
            documents_list.append(doc['text'])
            metadatas.append(doc.get('metadata', {}))
        
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents_list,
                metadatas=metadatas,
            )
            return ids
        except Exception as e:
            print(f"Error adding documents to ChromaDB: {e}")
            return []

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 3,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query the ChromaDB collection.
        
        Args:
            query_embedding: Embedding vector for the query
            top_k: Number of results to return
            where: Optional metadata filter (e.g., {"modality": {"$eq": "text"}})
            
        Returns:
            Query results with ids, distances, documents, metadatas
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["embeddings", "metadatas", "documents", "distances"]
            )
            return results
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}

    def get_all_documents(self) -> Dict:
        """
        Retrieve all documents from the collection.
        
        Returns:
            All documents with ids, documents, metadatas
        """
        try:
            return self.collection.get(
                include=["metadatas", "documents", "distances"]
            )
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return {"ids": [], "documents": [], "metadatas": []}

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False

    def clear_collection(self) -> bool:
        """
        Delete the entire collection.
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

    def count(self) -> int:
        """Get the number of documents in the collection."""
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error counting documents: {e}")
            return 0


if __name__ == "__main__":
    # Example usage
    db = ChromaDBManager()
    
    # Add sample documents
    sample_docs = [
        {
            "id": "doc_1",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "text": "This is the first document",
            "metadata": {"page": 1, "modality": "text"},
        },
        {
            "id": "doc_2",
            "embedding": [0.2, 0.3, 0.4, 0.5, 0.6],
            "text": "This is the second document",
            "metadata": {"page": 2, "modality": "text"},
        },
    ]
    
    db.add_documents(sample_docs)
    print(f"Documents in collection: {db.count()}")
    
    # Query
    results = db.query([0.1, 0.2, 0.3, 0.4, 0.5], top_k=2)
    print(f"Query results: {results}")
