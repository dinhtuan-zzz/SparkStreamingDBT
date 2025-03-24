from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from datagen import generate_data

app = FastAPI()


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


@app.get('/v2/random-data')
def random_data():
    return generate_data()


if __name__ == '__main__':
    uvicorn.run(app)
