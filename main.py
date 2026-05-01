from fastapi import FastAPI
from routes.route import router as approuter
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)


app.include_router(approuter)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
