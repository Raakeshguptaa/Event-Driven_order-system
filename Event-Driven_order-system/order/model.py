from pydantic import BaseModel

class Create_order(BaseModel):
    prod_name : str
    prod_id : int
    prod_quant : int


class Order(BaseModel):
    name:str
    user_id:int
    quantity : int

