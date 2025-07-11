import os
import firebase_admin
from firebase_admin import credentials, firestore

# Load credentials and initialize Firebase app
cred_file = os.getenv('FIREBASE_CREDENTIALS_FILE', './credentials/firebase_credentials_testing.json')
cred = credentials.Certificate(cred_file)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Set your player collection name here
PLAYER_COLLECTION = os.getenv('FIRESTORE_PLAYER_COLLECTION', 'players')

TEAM_ID_FIELD = 'team_id'
LEGACY_TEAM_IDS = [
    'old-guid-team-id',  # Add any known legacy GUIDs here
    # ...
]
NEW_TEAM_ID = 'KAI'

def correct_legacy_team_ids():
    print('🔄 Checking for legacy team IDs...')
    players_ref = db.collection(PLAYER_COLLECTION)
    docs = players_ref.stream()
    count = 0
    for doc in docs:
        data = doc.to_dict()
        if TEAM_ID_FIELD in data and data[TEAM_ID_FIELD] in LEGACY_TEAM_IDS:
            players_ref.document(doc.id).update({TEAM_ID_FIELD: NEW_TEAM_ID})
            print(f'✅ Updated team_id for player {doc.id} to {NEW_TEAM_ID}')
            count += 1
    print(f'🔍 Legacy team ID correction complete. {count} player(s) updated.')

def delete_all_players():
    print('⚠️  Deleting all player documents in Firestore collection:', PLAYER_COLLECTION)
    players_ref = db.collection(PLAYER_COLLECTION)
    docs = players_ref.stream()
    count = 0
    for doc in docs:
        players_ref.document(doc.id).delete()
        print(f'🗑️  Deleted player document: {doc.id}')
        count += 1
    print(f'✅ All player documents deleted. Total: {count}')

if __name__ == '__main__':
    correct_legacy_team_ids()
    delete_all_players()
    print('🎉 Firestore player data cleanup complete.') 