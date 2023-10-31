import argparse
from typing import List, Tuple

from fastapi import FastAPI

from constants import GET_WORDS_BY_THEME, GET_UNIQUE_THEMES, GET_WORD_DATA, CREATE_USER
from data import WordModel, GetWordData, CreateUser
from supabase_service import SupabaseService


def parse_args():
    parser = argparse.ArgumentParser(description='Upword API')
    parser.add_argument('--url', type=str, help='Supabase URL')
    parser.add_argument('--key', type=str, help='Supabase key')
    return parser.parse_args()


app = FastAPI()

args = parse_args()
supabase_service = SupabaseService(args.url, args.key)


@app.get(GET_UNIQUE_THEMES, response_model=List[str])
async def get_unique_themes():
    return supabase_service.get_unique_themes()


@app.get(GET_WORDS_BY_THEME)
async def get_words_by_theme(request: WordModel):
    return supabase_service.get_words_by_theme(request.theme)


@app.get(GET_WORD_DATA, response_model=Tuple[dict])
async def get_word_data(request: GetWordData):
    return supabase_service.get_word_data(request.word, request.theme)


@app.post(CREATE_USER)
async def create_user(request: CreateUser):
    return supabase_service.create_new_user(request.email, request.password, request.username, request.first_name,
                                            request.last_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
