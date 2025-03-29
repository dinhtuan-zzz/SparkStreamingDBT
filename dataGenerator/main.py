from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
import uvicorn
from datagen import generate_data

app = FastAPI()


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get('/v2/random-data-list')
def random_data_list(count: int = Query(1000, ge=1, le=100000, description="Number of data need to generated")):
    """
    Generate list of dataset.
    Default is 1000.
    """
    data_list = [generate_data() for _ in range(count)]
    return data_list
@app.get('/v2/random-data-single')
def random_data():
    """Generate single data"""
    return generate_data()


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
