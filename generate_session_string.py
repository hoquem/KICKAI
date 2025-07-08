import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Get API credentials from environment or prompt
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')

if not api_id:
    api_id = input('Enter your TELEGRAM_API_ID: ')
if not api_hash:
    api_hash = input('Enter your TELEGRAM_API_HASH: ')

print('--- Telegram Session String Generator ---')
phone = input('Enter the phone number (e.g. +447871521581): ')

print(f'\n🔐 Attempting to connect to Telegram for {phone}...')
print('📱 You should receive a Telegram code shortly...')

# Create client and start authentication
client = TelegramClient(StringSession(), int(api_id), api_hash)

try:
    # Start the client with the provided phone number
    client.start(phone=phone)
    
    print('\n✅ Session string generated successfully!')
    print('📋 Copy the following line and add to your .env.test file:')
    print('=' * 60)
    print(f'PLAYER_SESSION_STRING={client.session.save()}')
    print('=' * 60)
    
except Exception as e:
    print(f'\n❌ Error generating session string: {e}')
    print('Make sure the phone number is correct and you have access to the Telegram account.')

finally:
    client.disconnect() 