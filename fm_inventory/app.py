from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fm_inventory.routers.product_route import api_router as product_router
from fm_inventory.routers.cart_route import api_router as cart_router


def intialize_app():
    app = FastAPI()

    # include cors
    app.include_router(router=product_router)
    app.include_router(router=cart_router)
    return app


app = intialize_app()


@app.get("/", status_code=200)
def root_to_docs():
    return RedirectResponse(url="/docs", status_code=200)
