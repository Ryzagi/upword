# Define a model for the word data
from typing import Optional

from pydantic import BaseModel


class WordModel(BaseModel):
    theme: int


class GetWordData(BaseModel):
    theme: str
    word: str


class UpdateUser(BaseModel):
    user_id: str
    email: Optional[str]
    password: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class PutWordInFolder(BaseModel):
    word_id: int
    folder: str
    source: str


class CountWordsInFolderByUser(BaseModel):
    user_id: str


class GetWordsInFolderByUser(BaseModel):
    user_id: str
    folder_name: str


class ThemeWordsCount(BaseModel):
    theme: int
    user_id: str
