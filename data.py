# Define a model for the word data
from pydantic import BaseModel


class WordModel(BaseModel):
    theme: str


class GetWordData(BaseModel):
    theme: str
    word: str


class CreateUser(BaseModel):
    email: str
    password: str
    username: str
    first_name: str
    last_name: str

