import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = os.getenv('TELEGRAM_API_ID') or input('Enter your TELEGRAM_API_ID: ')
api_hash = os.getenv('TELEGRAM_API_HASH') or input('Enter your TELEGRAM_API_HASH: ')
session_string = os.getenv('ADMIN_SESSION_STRING') or input('Enter your session string: ')

print('--- Listing Telegram Chats for Session ---')

with TelegramClient(StringSession(session_string), int(api_id), api_hash) as client:
    print('\nAccessible chats:')
    for dialog in client.iter_dialogs():
        chat_type = type(dialog.entity).__name__
        print(f"ID: {dialog.id} | Type: {chat_type} | Title: {dialog.name}") 