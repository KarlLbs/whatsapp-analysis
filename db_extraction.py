"""
db_extraction.py

Provides a class to extract information (like a conversation history) from a msgstore database file.
"""

import sqlite3
import pandas as pd

class Extractor:
    '''
    Class to extract info from database files.
    '''
    def __init__(self, msgstore_path, wa_db_path=None):
        self.msgstore = msgstore_path
        self.wa_db = wa_db_path

    def _get_chat_id(self, chat_name:str) -> int :
        if type(chat_name) == str :
            conn = sqlite3.connect(str(self.msgstore))
            cur = conn.cursor()
            message_query = f"""SELECT chat._id FROM chat WHERE chat.subject = '{chat_name}'"""
            cur.execute(message_query)
            chat_id = cur.fetchall()[0][0]
            print(f"Conversation '{chat_name}' id :", chat_id)
            conn.close()
        else : 
            raise TypeError("Expected a string for the chat name.")
        return chat_id

    def extract_conversation(self, chat, phone_numbers_map=None) -> pd.DataFrame:
        '''
        Extracts a single chat_history from the msgstore database,
        and returns it as a pd dataframe with only useful columns.

        Args:
            chat (str or int): Name or id of the chat.
            phone_no_map (dict, optional) : a map of contacts' phone numbers and names.
        '''

        chat_id = self._get_chat_id(chat) if isinstance(chat,str) else chat
        conn = sqlite3.connect(str(self.msgstore))
        message_query = f""" 
            SELECT message.*, jid.user
            FROM message
            LEFT JOIN jid ON message.sender_jid_row_id = jid._id
            WHERE message.chat_row_id = {chat_id}
        """
        df = pd.read_sql_query(message_query, conn) # Execute the query and load the result into a pandas DataFrame
        conn.close()

        # Cleaning up columns
        df = df[['sender_jid_row_id', 'user', 'recipient_count', 'timestamp', 'message_type', 'text_data', 'starred', 'message_add_on_flags']]
        
        contacts_map = self.extract_contacts()
        if len(contacts_map) < len(df['user'].unique()) : # the contacts table of wa.db is empty or incomplete
            if phone_numbers_map : 
                df['user'] = df['user'].map(phone_numbers_map)
        else : 
            df['user'] = df['user'].map(contacts_map)
        return df


    def extract_contacts(self):
        '''
        Extract contacts phone numbers and names from the wa_contacts table of the wa.db database.
        '''

        if self.wa_db :
            try : 
                conn = sqlite3.connect(str(self.wa_db))
                cur = conn.cursor()
                message_query = "SELECT wa_contacts.jid, wa_contacts.display_name FROM wa_contacts"
                cur.execute(message_query)
                contacts = cur.fetchall()
                contacts_map = {i[0]:i[1] for i in contacts}
                print("Contacts : ", contacts_map)
                conn.close()
            except : print("error")
        else : 
            raise FileNotFoundError("No wa.db file provided.")
        return contacts_map 
    
    