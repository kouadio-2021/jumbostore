from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello Jumbostore"}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.get("/products")
def get_products():
    products = [
        {"id": 1, "name": "Chaussures BAODUC", "price": 25000},
        {"id": 2, "name": "Chemise noire manches longues", "price": 15000},
        {"id": 3, "name": "Parfum Dior Sauvage", "price": 60000},
    ]
    return products


