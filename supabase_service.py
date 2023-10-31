from typing import List

from supabase import create_client, Client


class SupabaseService:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_client: Client = create_client(supabase_url, supabase_key)
        self.words_table = 'words'
        self.users_table = 'users'

    def get_unique_themes(self) -> List[str]:
        response, error = self.supabase_client.table(self.words_table).select("theme").execute()
        name, data = response
        themes = list(set(entry['theme'] for entry in data))
        print(themes)
        return themes

    def get_words_by_theme(self, theme: str) -> List[dict]:
        response, error = self.supabase_client.table(self.words_table).select("word").eq("theme", theme).execute()
        name, words = response
        return words

    def get_word_data(self, word: str, theme: str) -> dict:
        response, error = self.supabase_client.table(self.words_table).select('*').eq('theme', theme).eq('word',
                                                                                                         word).execute()
        name, data = response
        word_data = data
        return word_data

    def create_new_user(self, user_email: str, user_password: str, username: str, first_name: str, last_name: str):
        is_user_exists = self.is_user_exists(user_email)
        is_username_exists = self.is_username_exists(username)
        print(is_user_exists, is_username_exists)

        if is_user_exists:
            return "User with this email already exists", 400
        if is_username_exists:
            return "User with this username already exists", 400

        data, count = self.supabase_client.table(self.users_table).insert(
            {
                "email": user_email,
                "password": user_password,
                "first_name": first_name,
                "last_name": last_name,
                "username": username
            }
        ).execute()
        print(data, count)
        response, error = self.supabase_client.auth.sign_up({"email": user_email, "password": user_password})
        print(response, error)
        return response, error

    def is_username_exists(self, username: str):
        response, error = self.supabase_client.table(self.users_table).select("username").eq("username", username).execute()
        name, data = response
        print(data)
        if data:
            return True
        else:
            return False

    def is_user_exists(self, user_email: str):
        response, error = self.supabase_client.table(self.users_table).select("email").eq("email", user_email).execute()
        name, data = response
        print(data)
        if data:
            return True
        else:
            return False
