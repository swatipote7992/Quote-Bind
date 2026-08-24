from pydantic import BaseModel, Field
from enum import Enum

class Category(str, Enum):
    veg = "Veg"
    nonveg = "Non-Veg"
    vegan = "Vegan"


class RecipeBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=200)
    category: Category
    cooking_time: int = Field(gt=0, le=60)


class RecipeCreate(RecipeBase):
    created_by: str | None = None  # Optional Field


class RecipeResponse(RecipeBase):
    id: str
    updated_by: str | None = Field(default=None)  # Another way for Optional Field