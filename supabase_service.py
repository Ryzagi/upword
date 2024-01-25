from collections import defaultdict
from typing import List, Tuple, Dict, Union

from supabase import create_client, Client


class SupabaseService:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_client: Client = create_client(supabase_url, supabase_key)
        self.words_table = 'words'
        self.users_table = 'users'
        self.theme_id_table = 'theme_table'
        self.bucket_name = 'pictures'

    def get_unique_themes(self) -> Dict:
        # Fetch themes and their IDs from the themes_table
        response, error = self.supabase_client.table(self.theme_id_table).select("id", "theme", "theme_ru",
                                                                                 "count_words").execute()
        data = response[1]

        themes = []
        for entry in data:
            theme_id = str(entry['id'])  # Assuming 'id' is an integer, converting it to string
            theme = entry['theme']
            russian_theme = entry['theme_ru']
            count_words = str(entry['count_words'])
            theme_info = {
                "id": theme_id,
                "count_words": count_words,
                "english_name": theme,
                "russian_name": russian_theme,
                "image_url": self.supabase_client.storage.from_(self.bucket_name).get_public_url(f"{theme}.png")
            }
            themes.append(theme_info)

        formatted_data = {"themes": themes}
        return formatted_data

    def count_rows_by_theme(self, theme: str) -> int:
        # Fetching the count of rows for a specific theme from the 'words' table
        response, error = self.supabase_client.from_('words').select("theme").eq('theme', theme).execute()

        count = len(response[1])
        return count

    def update_count_words_in_theme_table(self):
        # Fetching themes and their IDs from the theme_table
        response, error = self.supabase_client.table('theme_table').select("id", "theme").execute()
        print(response[1])
        themes = response[1]

        for theme_entry in themes:
            theme_id = theme_entry['id']
            theme_name = theme_entry['theme']

            # Fetching count of rows for the theme from the 'words' table
            row_count = self.count_rows_by_theme(theme_name)

            # Updating 'count_words' column in the 'theme_table' for each theme
            update_response, update_error = self.supabase_client.table('theme_table').update(
                {'count_words': row_count}).eq('id', theme_id).execute()

    def get_words_by_theme(self, theme_id: int) -> Dict:
        theme = self.get_theme_by_id(theme_id)
        response, error = self.supabase_client.table(self.words_table).select("id", "word", "transcription",
                                                                              "difficulty_level", "list_of_examples",
                                                                              "sentence_in_english",
                                                                              "sentence_in_russian",
                                                                              "translation_to_russian").eq("theme",
                                                                                                           theme).execute()
        return response[1]

    def get_theme_by_id(self, theme_id: int) -> str:
        response, error = self.supabase_client.table(self.theme_id_table).select("theme").eq("id",
                                                                                             theme_id).execute()
        print(response[1])
        return response[1][0]['theme']

    def get_word_data(self, word: str, theme: str) -> dict:
        response, error = self.supabase_client.table(self.words_table).select('*').eq('theme', theme).eq('word',
                                                                                                         word).execute()
        print(response)
        return response

    def create_new_user(self, user_email: str, user_password: str, username: str, first_name: str, last_name: str):
        is_user_exists = self.is_user_exists(user_email)
        is_username_exists = self.is_username_exists(username)
        print(is_user_exists, is_username_exists)

        if is_user_exists:
            return "User with this email already exists", 400
        if is_username_exists:
            return "User with this username already exists", 400

        data, error = self.supabase_client.table(self.users_table).insert(
            {
                "email": user_email,
                "password": user_password,
                "first_name": first_name,
                "last_name": last_name,
                "username": username
            }
        ).execute()
        print(data)
        response = self.supabase_client.auth.sign_up({"email": user_email, "password": user_password})
        print(response)
        return response

    def is_username_exists(self, username: str):
        response, error = self.supabase_client.table(self.users_table).select("username").eq("username",
                                                                                             username).execute()

        print(response)
        if response:
            return True
        else:
            return False

    def is_user_exists(self, user_email: str):
        response, error = self.supabase_client.table(self.users_table).select("email").eq("email",
                                                                                          user_email).execute()

        print(response)
        if response:
            return True
        else:
            return False

    def put_word_in_folder(self, user_id: str, word_id: str, folder_name: str):
        # Define the data to be inserted
        data = {
            'user_id': user_id,
            'word_id': word_id,
            # Add other columns if needed
        }
        response = self.supabase_client.table(folder_name).insert([data]).execute()

        return response

    def count_words_in_folder_by_user(self, user_id: str, folder_name: str) -> int:
        response, error = self.supabase_client.table(folder_name).select("word_id").eq("user_id",
                                                                                       user_id).execute()

        print(response)
        return len(response[1])


