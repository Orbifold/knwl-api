import asyncio
import time
from typing import Dict

from knwl import Knwl, KnwlInput, KnwlParams, KnwlAnswer, KnwlContext

from knwl_api.models.JobStatus import JobStatus, JobState
from knwl_api.models.KnwlFact import KnwlFact

knwl = Knwl()  # Initialize Knwl instance with default namespace

# In-memory job storage (in production, use Redis or a database)
jobs: Dict[str, JobStatus] = {}


async def add_job(job_type: str, data: dict) -> str:
    """Adds a new ingestion job to the job queue"""
    job_id = str(time.time())  # Simple job ID generation using timestamp
    jobs[job_id] = JobStatus(job_type=job_type, job_id=job_id, state=JobState.PENDING, created_at=time.time(), updated_at=time.time(), )
    if job_type == "ingest":
        input = KnwlInput(**data)
        asyncio.create_task(process_ingest_job(job_id, input))
    elif job_type == "fact":
        input = KnwlFact(**data)
        asyncio.create_task(process_fact_job(job_id, input))
    return job_id


async def get_job_status(job_id: str) -> JobStatus | None:
    """Retrieves the status of a given job"""
    return jobs.get(job_id)


async def process_ingest_job(job_id: str, input: KnwlInput):
    """Background task to process data ingestion"""
    try:
        # Update job state to running
        jobs[job_id].state = JobState.RUNNING
        jobs[job_id].updated_at = time.time()

        # Perform the actual ingestion
        result = await knwl.ingest(input)

        # Update job state to completed
        jobs[job_id].state = JobState.COMPLETED
        jobs[job_id].result = result.model_dump(mode="dict")
        jobs[job_id].updated_at = time.time()
    except Exception as e:
        # Update job state to failed
        jobs[job_id].state = JobState.FAILED
        jobs[job_id].error = str(e)
        jobs[job_id].updated_at = time.time()


async def process_fact_job(job_id: str, fact: KnwlFact):
    """Background task to process adding a fact"""
    try:
        # Update job state to running
        jobs[job_id].state = JobState.RUNNING
        jobs[job_id].updated_at = time.time()

        # Perform the actual fact addition
        result = await knwl.add_fact(name=fact.name, content=fact.content, type=fact.type, id=fact.id)

        # Update job state to completed
        jobs[job_id].state = JobState.COMPLETED
        jobs[job_id].result = result.model_dump(mode="dict")
        jobs[job_id].updated_at = time.time()
    except Exception as e:
        # Update job state to failed
        jobs[job_id].state = JobState.FAILED
        jobs[job_id].error = str(e)
        jobs[job_id].updated_at = time.time()


async def node_count() -> int:
    """Returns the count of nodes in the knowledge graph."""
    return await knwl.node_count()


async def edge_count() -> int:
    """Returns the count of edges in the knowledge graph."""
    return await knwl.edge_count()


async def get_namespace() -> str:
    """Returns the current namespace of the knowledge graph."""
    return knwl.namespace


async def get_node_by_id(id: str):
    """Retrieves a node by its Id."""
    return await knwl.get_node_by_id(id)


async def delete_node_by_id(id: str):
    """Deletes a node by its Id."""
    return await knwl.delete_node_by_id(id)


async def ask_question(question: str, strategy: str = None) -> KnwlAnswer:
    """
    Asks a question to the knowledge graph.
    """
    if strategy is None:
        strategy = KnwlParams.model_fields["strategy"].default
    input = KnwlInput(text=question, params=KnwlParams(strategy=strategy))
    return await knwl.ask(input)


async def augment(text: str, strategy: str = None) -> KnwlContext:
    """
    Augments the given text using the knowledge graph.k
    """
    if strategy is None:
        strategy = KnwlParams.model_fields["strategy"].default
    input = KnwlInput(text=text, params=KnwlParams(strategy=strategy))
    return await knwl.augment(input)
