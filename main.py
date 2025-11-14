if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(
        "knwl_api.main:app", host="0.0.0.0", port=9030, reload=True, workers=1
    )  # note that FastAPI reload only works with 1 worker
