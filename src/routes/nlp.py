from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from models import ProjectModel, ChunkModel
from controllers import NlpController
from routes.schema import PushRequest, SearchRequest

nlp_router = APIRouter()


@nlp_router.post("/index/push/{project_id}")
async def push_to_index(project_id: str, push_request: PushRequest, request: Request):

    project_model = ProjectModel(db_client=request.app.db_client)
    await project_model.get_project_or_create(project_id)

    chunk_model = ChunkModel(db_client=request.app.db_client)

    all_chunks = []
    page = 1
    while True:
        chunks = await chunk_model.get_chunks_by_project(
            project_id=project_id,
            page=page,
            page_size=50
        )
        if not chunks:
            break
        all_chunks.extend(chunks)
        page += 1

    if not all_chunks:
        return JSONResponse(status_code=400, content={
            "error": "No chunks found for this project"
        })

    nlp_controller = NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    count = nlp_controller.push_to_index(
        project_id=project_id,
        chunks=all_chunks,
        do_reset=push_request.do_reset
    )

    return JSONResponse(status_code=200, content={
        "message": f"Successfully pushed {count} chunks to the index"
    })


@nlp_router.get("/index/info/{project_id}")
async def get_index_info(project_id: str, request: Request):

    nlp_controller = NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    collection_name = nlp_controller.get_collection_name(project_id)
    exists = request.app.vectordb_client.is_collection_exists(collection_name)

    return JSONResponse(status_code=200, content={
        "project_id": project_id,
        "index_exists": exists
    })


@nlp_router.post("/index/search/{project_id}")
async def search_index(project_id: str, search_request: SearchRequest, request: Request):

    nlp_controller = NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    results, search_query = nlp_controller.search_with_language(
        project_id=project_id,
        query=search_request.text,
        top_k=search_request.top_k,
        language=search_request.language
    )

    if not results:
        return JSONResponse(status_code=404, content={
            "error": "No results found"
        })

    return JSONResponse(status_code=200, content={
        "search_query": search_query,
        "results": [
            {
                "text": r["doc"].text,
                "score": r["score"]
            }
            for r in results
        ]
    })


@nlp_router.post("/index/answer/{project_id}")
async def get_answer(project_id: str, search_request: SearchRequest, request: Request):

    nlp_controller = NlpController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser
    )

    answer, full_prompt, chat_history = nlp_controller.answer(
        project_id=project_id,
        query=search_request.text,
        top_k=search_request.top_k,
        language=search_request.language
    )

    if not answer:
        return JSONResponse(status_code=404, content={
            "error": "Could not generate an answer"
        })

    return JSONResponse(status_code=200, content={
        "answer": answer,
        "full_prompt": full_prompt,
        "chat_history": chat_history
    })
