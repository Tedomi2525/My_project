from fastapi import FastAPI

app = FastAPI(title="Online Exam System")

@app.get("/")
def root():
    return {"message": "FastAPI Exam System is running"}
