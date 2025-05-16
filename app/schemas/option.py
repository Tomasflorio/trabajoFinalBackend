from pydantic import BaseModel

class OptionBase(BaseModel):
    option_text: str

class OptionCreate(OptionBase):
    pass

class OptionOut(OptionBase):
    id: int

    class Config:
        from_attributes = True
