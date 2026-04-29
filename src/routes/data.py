import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from models import ProjectModel, ChunkModel
from controllers import DataController, FileController, ProcessController
from routes.schema.data import ProcessRequest

data_router = APIRouter()


@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str, file: UploadFile = File(...),
                      settings: Settings = Depends(get_settings),
                      request=None):

    # Step 1: validate the file type and size
    data_controller = DataController()
    is_valid, message = data_controller.validate_file(file)

    if not is_valid:
        return JSONResponse(status_code=400, content={"error": message})

    # Step 2: make sure the project exists in MongoDB
    project_model = ProjectModel(db_client=request.app.db_client)
    project = await project_model.get_project_or_create(project_id)

    # Step 3: save the file to disk
    file_controller = FileController()
    file_path = file_controller.get_file_path(project_id, file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        while True:
            chunk = await file.read(settings.FILE_CHUNK_SIZE)
            if not chunk:
                break
            await f.write(chunk)

    return JSONResponse(status_code=200, content={
        "message": "File uploaded successfully",
        "project_id": project_id,
        "file_name": file.filename
    })


@data_router.post("/process/{project_id}")
async def process_file(project_id: str, process_request: ProcessRequest = None,
                      request=None):

    # Step 1: get the project from MongoDB
    project_model = ProjectModel(db_client=request.app.db_client)
    project = await project_model.get_project_or_create(project_id)

    # Step 2: delete old chunks if do_reset is set
    chunk_model = ChunkModel(db_client=request.app.db_client)

    if process_request.do_reset == 1:
        await chunk_model.delete_chunks_by_project(project_id)

    # Step 3: load and split the file into chunks
    process_controller = ProcessController(project_id=project_id)
    chunks = process_controller.process_file(
        file_name=process_request.file_name,
        chunk_size=process_request.chunk_size,
        overlap=process_request.overlap
    )

    if chunks is None:
        return JSONResponse(status_code=400, content={"error": "Could not process file"})

    # Step 4: save the chunks to MongoDB
    count = await chunk_model.insert_many_chunks(chunks, project_id)

    return JSONResponse(status_code=200, content={
        "message": f"File processed successfully",
        "chunks_created": count
    })