import argparse

from fastapi import FastAPI, Query
from starlette import status
from starlette.responses import PlainTextResponse

from constants import GET_WORDS_BY_THEME, GET_UNIQUE_THEMES, GET_WORD_DATA, CREATE_USER, UPDATE_WORDS_COUNT, \
    PUT_WORD_IN_FOLDER, COUNT_WORDS_IN_FOLDERS_BY_USER, GET_WORDS_IN_FOLDER_BY_USER
from data import WordModel, GetWordData, CreateUser, PutWordInFolder, CountWordsInFolderByUser, GetWordsInFolderByUser
from supabase_service import SupabaseService


def parse_args():
    parser = argparse.ArgumentParser(description='Upword API')
    parser.add_argument('--host', type=str, help='Host')
    parser.add_argument('--url', type=str, help='Supabase URL')
    parser.add_argument('--key', type=str, help='Supabase key')
    return parser.parse_args()


app = FastAPI()

# args = parse_args()
supabase_service = SupabaseService("https://cjxpyxuygpvoyejcikwf.supabase.co",
                                   "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNqeHB5eHV5Z3B2b3llamNpa3dmIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTUxNDkwNzYsImV4cCI6MjAxMDcyNTA3Nn0._mfSXgRm0SSFrK3BG2B0GLAZAWvIcbDTK7njU-Io824")


# supabase_service = SupabaseService(args.url, args.key)


@app.get(GET_UNIQUE_THEMES)
async def get_unique_themes():
    return supabase_service.get_unique_themes()


@app.post("/health", status_code=status.HTTP_200_OK)
def root():
    return PlainTextResponse("OK")


@app.post(UPDATE_WORDS_COUNT)
def update_count_words_in_theme_table():
    supabase_service.update_count_words_in_theme_table()
    return PlainTextResponse("Updated")


@app.get("/items/")
async def words_by_theme(theme: int = Query(..., title="Theme ID", description="ID of the theme")):
    return {"words": supabase_service.get_words_by_theme(theme)}


@app.get(GET_WORD_DATA)
async def get_word_data(request: GetWordData):
    return supabase_service.get_word_data(request.word, request.theme)


@app.post(CREATE_USER)
async def create_user(request: CreateUser):
    return supabase_service.create_new_user(user_id=request.user_id, user_email=request.email, user_password=request.password,
                                            username=request.username, first_name=request.first_name,
                                            last_name=request.last_name)


@app.post(PUT_WORD_IN_FOLDER)
async def put_word_in_folder(request: PutWordInFolder):
    return supabase_service.put_word_in_folder(request.user_id, request.word_id, request.folder_name)


@app.get(COUNT_WORDS_IN_FOLDERS_BY_USER)
async def count_words_in_folder_by_user(request: CountWordsInFolderByUser):
    return supabase_service.count_words_in_folders_by_user(request.user_id)


@app.get(GET_WORDS_IN_FOLDER_BY_USER)
async def get_words_in_folder_by_user(request: GetWordsInFolderByUser):
    return supabase_service.get_words_in_folder_by_user(user_id=request.user_id, folder_name=request.folder_name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
