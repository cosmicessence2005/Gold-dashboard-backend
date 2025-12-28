from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "app is running"}

@app.get("/gold")
def gold():
    return {"message": "gold endpoint working"}

@app.get("/pressure")
def pressure():
    return {"message": "pressure endpoint working"}
