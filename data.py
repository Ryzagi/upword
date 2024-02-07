# Define a model for the word data
from pydantic import BaseModel


class WordModel(BaseModel):
    theme: int


class GetWordData(BaseModel):
    theme: str
    word: str


class UpdateUser(BaseModel):
    user_id: str
    email: str
    password: str
    username: str
    first_name: str
    last_name: str


class PutWordInFolder(BaseModel):
    user_id: str
    word_id: int
    folder_name: str


class CountWordsInFolderByUser(BaseModel):
    user_id: str


class GetWordsInFolderByUser(BaseModel):
    user_id: str
    folder_name: str
