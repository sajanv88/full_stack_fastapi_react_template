from pydantic import BaseModel


class ProductDto(BaseModel):
    id: str
    name: str
    description: str
    tax_code: str | None = None
    active: bool

class ProductListDto(BaseModel):
    products: list[ProductDto]
    has_more: bool


class CreateProductDto(BaseModel):
    name: str
    description: str
    tax_code: str | None = None
    active: bool = True
