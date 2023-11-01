import argparse
from typing import List, Tuple

from fastapi import FastAPI
from starlette import status
from starlette.responses import PlainTextResponse

from constants import GET_WORDS_BY_THEME, GET_UNIQUE_THEMES, GET_WORD_DATA, CREATE_USER
from data import WordModel, GetWordData, CreateUser
from supabase_service import SupabaseService


def parse_args():
    parser = argparse.ArgumentParser(description='Upword API')
    parser.add_argument('--host', type=str, help='Host')
    parser.add_argument('--url', type=str, help='Supabase URL')
    parser.add_argument('--key', type=str, help='Supabase key')
    return parser.parse_args()


app = FastAPI()

#args = parse_args()
supabase_service = SupabaseService("https://cjxpyxuygpvoyejcikwf.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqeHB5eHV5Z3B2b3llamNpa3dmIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTUxNDkwNzYsImV4cCI6MjAxMDcyNTA3Nn0._mfSXgRm0SSFrK3BG2B0GLAZAWvIcbDTK7njU-Io824")
#supabase_service = SupabaseService(args.url, args.key)


@app.get(GET_UNIQUE_THEMES, response_model=List[str])
async def get_unique_themes():
    return supabase_service.get_unique_themes()


@app.post("/health", status_code=status.HTTP_200_OK)
def root():
    return PlainTextResponse("OK")


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
