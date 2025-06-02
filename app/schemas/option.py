from pydantic import BaseModel

class OptionBase(BaseModel):
    option_text: str
    is_correct: bool

class OptionCreate(OptionBase):
    option_text: str
    is_correct: bool

class OptionOut(OptionBase):
    id: int

    class Config:
        from_attributes = True
