from models.DataBaseModel import DataBaseModel
from models.db_schemes.data_chunk import DataChunk


class ChunkModel(DataBaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client["chunks"]

    async def insert_many_chunks(self, chunks: list, project_id: str):
        chunk_documents = [
            {
                "chunk_text": chunk.page_content,
                "chunk_metadata": chunk.metadata,
                "chunk_order": i,
                "chunk_project_id": project_id
            }
            for i, chunk in enumerate(chunks)
        ]
        result = await self.collection.insert_many(chunk_documents)
        return len(result.inserted_ids)

    async def get_chunks_by_project(self, project_id: str, page: int = 1, page_size: int = 50):
        skip = (page - 1) * page_size
        cursor = self.collection.find(
            {"chunk_project_id": project_id}
        ).skip(skip).limit(page_size)

        results = await cursor.to_list(length=page_size)
        return [
            DataChunk(
                id=str(r["_id"]),
                chunk_text=r["chunk_text"],
                chunk_metadata=r["chunk_metadata"],
                chunk_order=r["chunk_order"],
                chunk_project_id=r["chunk_project_id"]
            )
            for r in results
        ]

    async def delete_chunks_by_project(self, project_id: str):
        result = await self.collection.delete_many(
            {"chunk_project_id": project_id}
        )
        return result.deleted_count