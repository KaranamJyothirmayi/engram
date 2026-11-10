import uuid

import chromadb


class VectorIndex:
    def __init__(self, persist_directory: str | None = None):
        if persist_directory:
            self._client = chromadb.PersistentClient(path=persist_directory)
            collection_name = "engram"
        else:
            self._client = chromadb.EphemeralClient()
            # Use a unique collection name so that separate VectorIndex()
            # instances (e.g. per-test fixtures) don't share state.
            # ChromaDB 1.5.9 EphemeralClient instances share a global
            # in-memory store, so a fixed name would bleed across tests.
            collection_name = f"engram_{uuid.uuid4().hex}"
        self._collection = self._client.get_or_create_collection(
            collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, memory_id: str, text: str, dataset: str):
        self._collection.upsert(
            ids=[memory_id],
            documents=[text],
            metadatas=[{"dataset": dataset}],
        )

    def search(self, query: str, datasets: list[str] | None, top_k: int = 5) -> list[dict]:
        count = self._collection.count()
        if count == 0:
            return []
        where = {"dataset": {"$in": datasets}} if datasets else None
        results = self._collection.query(
            query_texts=[query],
            n_results=min(top_k, count),
            where=where,
        )
        return [
            {"id": id_, "text": doc, "score": max(0.0, 1.0 - dist)}
            for id_, doc, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
            )
        ]

    def delete_by_dataset(self, dataset: str):
        results = self._collection.get(where={"dataset": dataset})
        if results["ids"]:
            self._collection.delete(ids=results["ids"])

    def delete_by_ids(self, ids: list[str]):
        if ids:
            self._collection.delete(ids=ids)
