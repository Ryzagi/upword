from typing import List, Tuple

from supabase import create_client, Client


class SupabaseService:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_client: Client = create_client(supabase_url, supabase_key)
        self.words_table = 'words'
        self.users_table = 'users'

    def get_unique_themes(self) -> List[str]:
        response, error, obj = self.supabase_client.table(self.words_table).select("theme").execute()
        name, data = response
        themes = list(set(entry['theme'] for entry in data))
        print(themes)
        return themes

    def get_words_by_theme(self, theme: str) -> Tuple[List[str]]:
        response, error, obj = self.supabase_client.table(self.words_table).select("word").eq("theme", theme).execute()
        print(response)
        # for entry in response:
        #    print(entry)
        # data, error = response
        # print(data, error)
        return response

    def get_word_data(self, word: str, theme: str) -> dict:
        response, error, obj = self.supabase_client.table(self.words_table).select('*').eq('theme', theme).eq('word',
                                                                                                              word).execute()
        print(response[1:])
        return response[1:]

    def create_new_user(self, user_email: str, user_password: str, username: str, first_name: str, last_name: str):
        is_user_exists = self.is_user_exists(user_email)
        is_username_exists = self.is_username_exists(username)
        print(is_user_exists, is_username_exists)

        if is_user_exists:
            return "User with this email already exists", 400
        if is_username_exists:
            return "User with this username already exists", 400

        data, error, obj = self.supabase_client.table(self.users_table).insert(
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
        response, error, obj = self.supabase_client.table(self.users_table).select("username").eq("username", username).execute()

        print(response)
        if response:
            return True
        else:
            return False

    def is_user_exists(self, user_email: str):
        response, error, obj = self.supabase_client.table(self.users_table).select("email").eq("email", user_email).execute()

        print(response)
        if response:
            return True
        else:
            return False
