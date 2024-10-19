from fastapi import FastAPI

app = FastAPI()

@app.router.get("/")
async def root():
    return {"yolo":"yolo"}