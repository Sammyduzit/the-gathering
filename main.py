from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from The Gathering!"}

@app.get("/test")
def test_endpoint():
    return {"status": "FastAPI works!", "project": "The Gathering"}