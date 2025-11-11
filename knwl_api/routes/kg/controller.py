from fastapi import APIRouter, HTTPException
from fastapi import Request

from knwl_api.models.JobStatus import JobStatus, JobResponse
from knwl_api.routes.kg import service

router = APIRouter()


@router.get("/node_count", description="Returns the amount of nodes.")
async def get_node_count(request: Request):
    try:
        return await service.node_count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edge_count", description="Returns the amount of edges.")
async def get_edge_count(request: Request):
    try:
        return await service.edge_count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/namespace", description="Returns the current namespace.")
async def get_namespace(request: Request):
    try:
        return await service.get_namespace()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node/{id}", description="Retrieves a node by its Id.")
async def get_node_by_id(id: str):
    try:
        node = await service.get_node_by_id(id)
        return node
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/node/{id}", description="Deletes a node by its Id.")
async def delete_node_by_id(id: str):
    try:
        return await service.delete_node_by_id(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", description="Ingests data into the knowledge graph.", response_model=JobResponse)
async def ingest_data(request: Request):
    try:
        data = await request.json()
        if not "text" in data:
            raise HTTPException(status_code=400, detail="Missing 'text' field in request body")
        job_id = await service.add_job("ingest", **data)

        return JobResponse(job_id=job_id, message="Ingestion job started successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}", description="Get the status of a job.", response_model=JobStatus)
async def get_job_status(job_id: str):
    try:
        status = await service.get_job_status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fact", description="Adds a fact to the knowledge graph.", response_model=JobResponse)
async def add_fact(request: Request):
    try:
        data = await request.json()
        if not "name" in data:
            raise HTTPException(status_code=400, detail="Missing 'name' of the fact in request body.")
        if not "content" in data:
            raise HTTPException(status_code=400, detail="Missing 'content' of the fact in request body.")
        if not "type" in data:
            raise HTTPException(status_code=400, detail="Missing 'type' of the fact in request body.")
        job_id = await service.add_job("fact", data)

        return JobResponse(job_id=job_id, message="Fact job started successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
