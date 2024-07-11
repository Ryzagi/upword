from collections import defaultdict
import random
from typing import List, Tuple, Dict, Union

from supabase import create_client, Client


class SupabaseService:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_client: Client = create_client(supabase_url, supabase_key)
        self.words_table = 'words'
        self.users_table = 'users'
        self.theme_id_table = 'theme_table'
        self.bucket_name = 'pictures'
        self.words_status_table = 'words_status'

    def get_unique_themes(self, user_id: str) -> Dict:
        # First query to get theme data
        response, error = self.supabase_client.table(self.theme_id_table).select("id", "theme", "theme_ru",
                                                                                 "count_words").execute()
        data = response[1]

        # Second query to get user-specific theme data
        response_user, error_user = self.supabase_client.table(self.words_status_table).select("theme").eq("user_id",
                                                                                                           user_id).execute()
        user_data = response_user[1]

        # Count occurrences of themes for the user
        theme_count = {}
        for entry_user in user_data:
            theme = entry_user['theme']
            if theme in theme_count:
                theme_count[theme] += 1
            else:
                theme_count[theme] = 1

        themes = []
        for entry in data:
            theme_id = str(entry['id'])
            theme = entry['theme']
            russian_theme = entry['theme_ru']
            default_count_words = entry['count_words']

            # Calculate the count of occurrences of the theme for the user
            count_words = theme_count.get(theme, 0)
            actually_count_words = default_count_words - count_words

            theme_info = {
                "id": theme_id,
                "count_words": str(actually_count_words),
                "english_name": theme,
                "russian_name": russian_theme,
                "image_url": self.supabase_client.storage.from_(self.bucket_name).get_public_url(f"themes/{theme.replace(' ', '_')}.png")
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
        # Iterate over each dictionary in the list and add the "url" key
        for item in response[1]:
            word = item["word"]
            sentence_in_english = item["sentence_in_english"]
            chars_to_remove = ",.!?;:"
            clean_text = sentence_in_english.translate(str.maketrans('', '', chars_to_remove))
            item["image_url"] = self.supabase_client.storage.from_(self.bucket_name).get_public_url(
                f"{theme}/{word}_{clean_text}.png")
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

    def create_new_user(self):
        data, error = self.supabase_client.table(self.users_table).insert(
            {
                "email": "",
                "password": "",
                "first_name": "",
                "last_name": "",
                "username": ""
            }
        ).execute()
        print(data)

        return {"id": data[1][0]["id"], "user_id": data[1][0]['user_id']}

    def update_user(self, user_id: str, user_email: str, user_password: str, username: str, first_name: str,
                    last_name: str):
        if len(user_id) > 0 or len(user_email) > 0:
            is_email_exists = self.is_email_exists(user_email)
            is_user_id_exists = self.is_user_id_exists(user_id)
            is_username_exists = self.is_username_exists(username)
            print(is_email_exists, is_username_exists)
            if is_email_exists:
                return "User with this email already exists", 400
            # if is_username_exists:
            #    return "User with this username already exists", 400
            if is_user_id_exists:
                self.supabase_client.table(self.users_table).update(
                    {
                        "email": user_email,
                        "password": user_password,
                        "first_name": first_name,
                        "last_name": last_name,
                        "username": username
                    }
                ).eq("user_id", user_id).execute()
                return "User updated successfully", 200
            # response = self.supabase_client.auth.sign_up({"email": user_email, "password": user_password})

    def is_user_id_exists(self, user_id: str):
        response, error = self.supabase_client.table(self.users_table).select("user_id").eq("user_id",
                                                                                            user_id).execute()

        print(response)
        if len(response[1]) > 0:
            return True
        else:
            return False

    def is_username_exists(self, username: str):
        response, error = self.supabase_client.table(self.users_table).select("username").eq("username",
                                                                                             username).execute()

        print(response)
        if len(response[1]) > 0:
            return True
        else:
            return False

    def is_email_exists(self, user_email: str):
        response, error = self.supabase_client.table(self.users_table).select("email").eq("email",
                                                                                          user_email).execute()

        print(response)
        if len(response[1]) > 0:
            return True
        else:
            return False

    def put_word_in_folder(self, user_id: str, word_id: int, folder_name: str, source: str):
        # Define the data to be inserted
        data = {
            'user_id': user_id,
            'word_id': word_id,

        }
        folders = ["learn", "repeat", "know"]
        if source not in folders:
            response = self.supabase_client.table(folder_name).insert([data]).execute()
            self.put_word_in_words_status(user_id=user_id, folder_name=folder_name, word_id=word_id)
        else:
            response = self.supabase_client.table(folder_name).insert([data]).execute()
            self.put_word_in_words_status(user_id=user_id, folder_name=folder_name, word_id=word_id)
            self.delete_word_in_folder(user_id=user_id, word_id=word_id, source_folder_name=source)
            self.delete_word_in_folder(user_id=user_id, word_id=word_id, source_folder_name=self.words_status_table)
        return response

    def count_words_in_folder_by_user(self, user_id: str, folder_name: str) -> int:
        response, error = self.supabase_client.table(folder_name).select("word_id").eq("user_id",
                                                                                       user_id).execute()

        return len(response[1])

    def count_words_in_folders_by_user(self, user_id: str) -> Dict[str, int]:
        folder_names, error = self.supabase_client.table('folders').select("folder_name").execute()
        folder_names = [folder['folder_name'].strip() for folder in folder_names[1]]
        counts = defaultdict(int)
        for folder_name in folder_names:
            counts[folder_name] = self.count_words_in_folder_by_user(user_id, folder_name)
        return counts

    def get_ids_in_folder_by_user(self, user_id: str, folder_name: str) -> List[int]:
        response, error = self.supabase_client.table(folder_name).select("word_id").eq("user_id",
                                                                                       user_id).execute()
        return [entry['word_id'] for entry in response[1]]

    def get_words_by_ids(self, ids: List[int]) -> List[Dict]:
        response = self.supabase_client.table(self.words_table).select("id", "word", "transcription", "theme",
                                                                              "difficulty_level", "list_of_examples",
                                                                              "sentence_in_english",
                                                                              "sentence_in_russian",
                                                                              "translation_to_russian","eng_ru_sentences").in_("id",
                                                                                                            ids).execute()

        # Iterate over each dictionary in the list and add the "url" key
        for item in response.data:
            word = item["word"].replace(" ", "_")
            theme = item["theme"]
            sentence_in_english = item["sentence_in_english"]
            chars_to_remove = ",.!?;:"
            clean_text = sentence_in_english.translate(str.maketrans('', '', chars_to_remove)).replace(" ", "_")
            item["image_url"] = self.supabase_client.storage.from_(self.bucket_name).get_public_url(
                f"{theme}/{word}_{clean_text}.png")
            sentences_transformed = [{"eng": sentence[0], "rus": sentence[1]} for sentence in
                                     item.get("eng_ru_sentences", [])]
            item["sentences"] = sentences_transformed
            # Remove the original eng_ru_sentences field
            if "eng_ru_sentences" in item:
                del item["eng_ru_sentences"]
        return response.data

    def extend_list_until_length_is_n(self, n: int, words_list: List[str], distractors_list: List[str]) -> List[str]:
        """
        Extend the first list with elements from the second list until the length of the first list is equal to n.
        Args:
            n: The desired length of the first list
            words_list: The list to be extended
            distractors_list: The list to draw elements from
        Returns:
            Extended list
        """
        # Calculate the number of elements needed
        needed_elements = n - len(words_list)

        # Extend the first list with the required number of elements from the second list
        if needed_elements > 0:
            words_list.extend(distractors_list[:needed_elements])
        return words_list

    def get_words_in_folder_by_user(self, user_id: str, folder_name: str) -> List[Dict]:
        ids = self.get_ids_in_folder_by_user(user_id, folder_name)
        if folder_name == "learn":
            words = self.get_words_by_ids(ids)
            for word_dict in words:
                word_list = [word["word"] for word in words if word["word"] != word_dict["word"]]
                # Add words until we have at least 4 words
                distractors_count = 4
                if len(word_list) < distractors_count:
                    distractors = ['A', 'It', 'Is', 'And']
                    word_list = self.extend_list_until_length_is_n(n=distractors_count, words_list=word_list,
                                                                   distractors_list=distractors)
                # Ensure we do not attempt to sample more words than are available
                word_dict["wrong_words"] = word_list
                # Ensure we do not attempt to sample more words than are available
                sample_size = min(3, len(word_list))
                wrong_words = random.sample(word_list, sample_size)
                word_dict["wrong_words"] = wrong_words
            return words
        return self.get_words_by_ids(ids)

    def get_theme_by_word_id(self, word_id: int) -> str:
        response, error = self.supabase_client.table(self.words_table).select("theme").eq("id",
                                                                                          word_id).execute()
        return response[1][0]['theme']

    def count_words_in_words_status_by_user_and_theme(self, user_id: str, theme: str) -> int:
        response, error = self.supabase_client.table(self.words_status_table).select("word_id").eq("user_id",
                                                                                                   user_id).eq("theme",
                                                                                                               theme).execute()
        return len(response[1])

    def count_real_words_by_theme(self, user_id: str, theme: int) -> int:
        theme = self.get_theme_by_id(theme)
        # get count_words from theme_table
        response, error = self.supabase_client.table(self.theme_id_table).select("count_words").eq("theme",
                                                                                                   theme).execute()
        default_theme_count_words = response[1][0]['count_words']
        print(theme)
        print(default_theme_count_words)
        # get count_words from words_status
        response, error = self.supabase_client.table(self.words_status_table).select("word_id").eq("user_id",
                                                                                                   user_id).eq("theme",
                                                                                                               theme).execute()
        count_words = len(response[1])
        print(count_words)
        actually_count_words = default_theme_count_words - count_words
        return actually_count_words

    def put_word_in_words_status(self, user_id: str, folder_name: str, word_id: int):

        theme = self.get_theme_by_word_id(word_id)

        data = {
            'user_id': user_id,
            'word_id': word_id,
            'theme': theme,
            'folder_name': folder_name

        }
        response = self.supabase_client.table(self.words_status_table).insert([data]).execute()
        return response

    def get_ids_except_ids_(self, ids: List[int]) -> List[int]:
        response, error = self.supabase_client.table(self.words_table).select("id").neq("id", ids).execute()
        return [entry['id'] for entry in response[1]]

    def get_ids_except_ids(self, ids: List[int], theme: str) -> List[int]:
        response, error = self.supabase_client.table(self.words_table).select("id").not_.in_("id", ids).eq("theme",
                                                                                                           theme).execute()
        return [entry['id'] for entry in response[1]]

    def get_word_ids_from_status_table(self, user_id: str, theme: str) -> List[int]:
        response, error = self.supabase_client.table(self.words_status_table).select("word_id").eq("user_id",
                                                                                                   user_id).eq("theme",
                                                                                                               theme).execute()
        return [entry['word_id'] for entry in response[1]]

    def get_words_by_theme_except_ids(self, user_id: str, theme: int) -> List[Dict]:
        theme = self.get_theme_by_id(theme)
        word_ids = self.get_word_ids_from_status_table(user_id, theme)
        ids = self.get_ids_except_ids(word_ids, theme)
        words = self.get_words_by_ids(ids)
        return words

    def delete_all_words_by_user(self, user_id: str):
        folders = ["learn", "repeat", "know"]
        for folder in folders:
            response, error = self.supabase_client.table(folder).delete().eq("user_id", user_id).execute()
        response, error = self.supabase_client.table(self.words_status_table).delete().eq("user_id", user_id).execute()
        return response

    def delete_word_in_folder(self, user_id: str, word_id: int, source_folder_name: str):
        response, error = self.supabase_client.table(source_folder_name).delete().eq("user_id", user_id).eq("word_id", word_id).execute()
        return response
