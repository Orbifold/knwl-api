from uuid import uuid4

from tests.fixtures import *


@pytest.mark.asyncio
async def test_facts(client):
    previous_count = client.get("/kg/node_count").json()
    id = str(uuid4())
    fact_data = {"name": "Test Fact", "content": "This is a test fact content.", "type": "test_type", "id": id}
    response = client.post("/kg/fact", json=fact_data)
    assert response.status_code == 200
    job = response.json()  # Get the job response
    job_id = job["job_id"]
    # Poll for job completion
    import time
    for _ in range(20):
        job_status_response = client.get(f"/kg/job/{job_id}")
        assert job_status_response.status_code == 200
        job_status = job_status_response.json()
        if job_status["state"] == "completed":
            break
        elif job_status["state"] == "failed":
            pytest.fail(f"Fact addition job failed with error: {job_status.get('error')}")
        time.sleep(1)
    else:
        pytest.fail("Fact addition job did not complete in expected time.")

    node_id = job_status["result"]["id"]
    assert node_id == fact_data["id"]
    # Test retrieving the node by ID
    response = client.get(f"/kg/node/{fact_data['id']}")
    assert response.status_code == 200
    retrieved_fact = response.json()
    assert retrieved_fact["name"] == fact_data["name"]
    assert retrieved_fact["description"] == fact_data["content"]
    assert retrieved_fact["type"] == fact_data["type"]
    assert retrieved_fact["id"] == fact_data["id"]
    current_count = client.get("/kg/node_count").json()
    assert current_count == previous_count + 1
    client.delete(f"/kg/node/{fact_data['id']}")
    current_count = client.get("/kg/node_count").json()
    assert current_count == previous_count

    job_status_response = client.get(f"/kg/job/abcdefg12345")
    assert job_status_response.status_code == 404 # job not found
