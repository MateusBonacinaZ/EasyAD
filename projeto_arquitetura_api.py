# IMPORTANDO AS BIBLIOTECAS
from fastapi import FastAPI, Body
from fastapi.encoders import *
from pydantic import BaseModel, Field
from bson import ObjectId
import motor.motor_asyncio

# INCIALIZANDO APLICATIVO E REALIZANDO COM O BANCO DE DADOS
app = FastAPI()
MONGO_ATLAS = 'mongodb+srv://apiuser:bdag2018@easyad.4hib5tt.mongodb.net/?retryWrites=true&w=majority'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_ATLAS)
banco = client.easyad

# COLETANDO AS COLEÇÕES
collection_easyad = banco.get_collection("ads")


# DEFININDO O ESQUEMA DE CATEGORIA
class Categoria(BaseModel):
    categoria: str = Field(...)


# DEFININDO O ESQUEMA DE USUÁRIO INTERNO
class UsuarioInterno(BaseModel):
    nome_anunciante: str = Field(...)
    email_anunciante: str = Field(...)
    telefone_anunciante: str = Field(...)
    senha_anunciante: str = Field(...)


# DEFININDO O ESQUEMA DE ANUNCIO
class Anuncio(BaseModel):
    titulo_produto: str = Field(...)
    descricao_produto: str = Field(...)
    localidade_produto: str = Field(...)
    valor_produto: float = Field(...)
    imagem_produto: str = Field(...)
    categoria_anuncio: Categoria = Field(...)
    usuario_interno: UsuarioInterno = Field(...)


# CONVERTER COLEÇÕES PARA DICIONÁRIOS PYTHON
def convert_ads_get(ads) -> dict:
    return {
        'id': str(ads["_id"]),
        'titulo_produto': ads["titulo_produto"],
        'descricao_produto': ads["descricao_produto"],
        'localidade_produto': ads["localidade_produto"],
        'valor_produto': ads["valor_produto"],
        'imagem_produto': ads["imagem_produto"],
        'categoria_anuncio': ads['categoria_anuncio']['categoria'],
        'nome_anunciante': ads['usuario_interno']['nome_anunciante'],
        'email_anunciante': ads['usuario_interno']['email_anunciante'],
        'telefone_anunciante': ads['usuario_interno']['telefone_anunciante']     
    }

# ->  ENDPOINTS DE ANUNCIOS  <-

# ROUTE - INSERT ADS
@app.post("/anuncios")
async def insert_ads_route(ads: Anuncio = Body(...)):
    ads_insert = jsonable_encoder(ads)
    new_ads = await insert_ads(ads_insert)
    return new_ads


# METHOD - INSERT ADS
async def insert_ads(data_ads: dict) -> dict:
    ads = await collection_easyad.insert_one(data_ads)
    new_ads = await collection_easyad.find_one({"_id": ads.inserted_id})
    return convert_ads_get(new_ads)


# ROUTE - GET ADS QUANTITY
@app.get("/anuncios")
async def get_ads_quantity_route(quantity: dict = Body(...)):
    ads = await get_ads_quantity(quantity['quantity'])
    return ads


# METHOD - GET ADS QUANTITY
async def get_ads_quantity(quantity: int) -> list:
    ads = []
    counter: int = len(ads)
    async for register in collection_easyad.find({}, {'usuario_interno': {'senha_anunciante': 0}}):
        ads.append(convert_ads_get(register))
        counter += 1
        if counter >= quantity:
            break
    return ads


# ROUTE - GET ADS BY ID
@app.get("/anuncios/{category}")
async def get_ads_category_route(category: str):
    ads = await get_ads_category(category)
    return ads


# METHOD - GET ADS ID
async def get_ads_category(category: str) -> list:
    ads = []
    async for register in collection_easyad.find({'categoria_anuncio': {'categoria': category}}):
        ads.append(convert_ads_get(register))
    return ads