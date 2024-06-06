import argparse

from fastapi import FastAPI, Query, Header, HTTPException
from starlette import status
from starlette.responses import PlainTextResponse

from constants import GET_WORDS_BY_THEME, GET_UNIQUE_THEMES, GET_WORD_DATA, CREATE_USER, UPDATE_WORDS_COUNT, \
    PUT_WORD_IN_FOLDER, GET_WORDS_FROM_FOLDER_BY_USER, COUNT_WORDS_IN_FOLDER_BY_USER, UPDATE_USER_INFO, SUPABASE_URL, \
    SUPABASE_KEY, COUNT_REAL_WORDS_BY_THEME, DELETE_WORDS_FROM_FOLDER
from data import WordModel, GetWordData, PutWordInFolder, CountWordsInFolderByUser, GetWordsInFolderByUser, \
    UpdateUser, ThemeWordsCount
from supabase_service import SupabaseService


def parse_args():
    parser = argparse.ArgumentParser(description='Upword API')
    parser.add_argument('--host', type=str, help='Host')
    parser.add_argument('--url', type=str, help='Supabase URL')
    parser.add_argument('--key', type=str, help='Supabase key')
    return parser.parse_args()


app = FastAPI()

# args = parse_args()
supabase_service = SupabaseService(SUPABASE_URL, SUPABASE_KEY)


@app.get(GET_UNIQUE_THEMES)
async def get_unique_themes(user_id: str = Header(...)):
    return supabase_service.get_unique_themes(user_id=user_id)


@app.post("/health", status_code=status.HTTP_200_OK)
def root():
    return PlainTextResponse("OK")


@app.post(UPDATE_WORDS_COUNT)
def update_count_words_in_theme_table():
    supabase_service.update_count_words_in_theme_table()
    return PlainTextResponse("Updated")


@app.get(GET_WORDS_BY_THEME)
async def words_by_theme(theme: int = Query(..., title="Theme", description="Theme of the words"),
                         user_id: str = Header(..., title="User ID", description="ID of the user")):
    get_words_by_theme_except_ids = supabase_service.get_words_by_theme_except_ids(theme=theme, user_id=user_id)
    return {"words": get_words_by_theme_except_ids}


@app.get(GET_WORD_DATA)
async def get_word_data(request: GetWordData):
    return supabase_service.get_word_data(request.word, request.theme)


@app.get(CREATE_USER)
async def create_user():
    return supabase_service.create_new_user()


@app.post(UPDATE_USER_INFO)
async def update_user(request: UpdateUser):
    return supabase_service.update_user(user_id=request.user_id, user_email=request.email,
                                        user_password=request.password,
                                        username=request.username, first_name=request.first_name,
                                        last_name=request.last_name)


@app.post(PUT_WORD_IN_FOLDER)
async def put_word_in_folder(request: PutWordInFolder, user_id: str = Header(...)):
    return supabase_service.put_word_in_folder(user_id=user_id, word_id=request.word_id, folder_name=request.folder, source=request.source)


@app.get(COUNT_WORDS_IN_FOLDER_BY_USER)
async def count_words_in_folder_by_user(user_id: str = Header(...)):
    return supabase_service.count_words_in_folders_by_user(user_id=user_id)


@app.get(GET_WORDS_FROM_FOLDER_BY_USER)
async def get_words_in_folder_by_user(folder: str = Query(...), user_id: str = Header(...)):
    return {"words": supabase_service.get_words_in_folder_by_user(user_id=user_id, folder_name=folder)}


@app.get(COUNT_REAL_WORDS_BY_THEME)
async def count_real_words_by_theme(user_id: str = Header(...), theme: int = Query(...)):
    return supabase_service.count_real_words_by_theme(user_id=user_id, theme=theme)


@app.get(DELETE_WORDS_FROM_FOLDER)
async def delete_words(user_id: str = Header(...)):
    return supabase_service.delete_all_words_by_user(user_id=user_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
