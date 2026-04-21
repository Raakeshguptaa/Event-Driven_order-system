from pydantic import BaseModel

class InventoryCreate(BaseModel):
    prod_name: str
    prod_quant: int

class InventoryUpdate(BaseModel):
    prod_id: int
    prod_quant: int