from fastapi import FastAPI
from routes.route import router as approuter
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
origins = [
    "https://make-my-trip-300.netlify.app"
]

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
