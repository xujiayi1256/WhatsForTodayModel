from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
def index():
    return {"greeting": "Hello world"}


@app.get("/get")
def get(cuisine=None, area=None):
    if not cuisine and not area:
        raise HTTPException(status_code=400, detail="Cuisine or area is required")

    result = {'data': {
        'cuisine': cuisine,
        'area': area
    }}
    print(result)
    return result
