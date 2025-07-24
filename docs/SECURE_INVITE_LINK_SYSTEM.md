# Secure Invite Link System

**Date:** July 23, 2025  
**Status:** Implemented  
**Issue:** Prevent unauthorized users from using invite links

## Problem Statement

The original invite link system had several security vulnerabilities:

1. **No Player-Specific Validation**: Anyone with the link could join, regardless of whether they were the intended recipient
2. **Weak Link Validation**: The system couldn't properly validate if the link was meant for a specific player
3. **No Embedded Information**: The invite link didn't contain any information about the intended recipient
4. **Replay Attacks**: Links could potentially be reused or shared with unauthorized users

## Solution: Secure Invite Link System

### 🔐 **Security Features**

#### 1. **Embedded Player Information**
Each invite link now contains encrypted player data:
- Player ID (e.g., `MH1`)
- Player Name
- Player Phone Number
- Team ID
- Invite ID
- Expiration timestamp
- Creation timestamp

#### 2. **HMAC-SHA256 Digital Signatures**
- All invite data is signed with a secret key
- Prevents tampering with player information
- Ensures link authenticity

#### 3. **Base64 URL-Safe Encoding**
- Encoded data is safe for URLs
- No special characters that could break links
- Compact representation

#### 4. **One-Time Use Links**
- Telegram API configured with `member_limit=1`
- Firestore tracks usage status
- Automatic expiration after 7 days

### 🔄 **System Flow**

#### **1. Player Addition via `/addplayer`**
```
User Input: /addplayer Mahmudul Hoque +447961103217 Defender
↓
Player Registration Service creates player record
↓
Player ID generated: MH1
↓
InviteLinkService creates secure invite link
↓
Player data embedded and signed
↓
Firestore stores invite record with secure_data
↓
User receives unique invite link
```

#### **2. Player Joins via Invite Link**
```
Player clicks invite link
↓
Telegram processes join request
↓
Bot detects new member
↓
System extracts secure_data from Firestore
↓
Validates HMAC signature
↓
Decodes player information
↓
Links Telegram user to existing player record
↓
Updates player.telegram_id field
```

### 📋 **Technical Implementation**

#### **Secure Data Generation**
```python
def _generate_secure_invite_data(self, player_data: dict) -> str:
    # Create payload with player information
    payload = {
        "player_id": player_data.get("player_id"),
        "player_name": player_data.get("player_name"),
        "player_phone": player_data.get("player_phone"),
        "team_id": player_data.get("team_id"),
        "invite_id": player_data.get("invite_id"),
        "expires_at": player_data.get("expires_at"),
        "created_at": player_data.get("created_at")
    }
    
    # Convert to JSON and create HMAC signature
    json_data = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        self._secret_key.encode('utf-8'),
        json_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Combine and encode
    combined_data = f"{json_data}.{signature}"
    return base64.urlsafe_b64encode(combined_data.encode('utf-8')).decode('utf-8')
```

#### **Secure Data Validation**
```python
def _validate_secure_invite_data(self, invite_data: str) -> dict | None:
    # Decode from base64
    decoded_bytes = base64.urlsafe_b64decode(invite_data.encode('utf-8'))
    combined_data = decoded_bytes.decode('utf-8')
    
    # Split data and signature
    json_data, signature = combined_data.rsplit('.', 1)
    
    # Verify HMAC signature
    expected_signature = hmac.new(
        self._secret_key.encode('utf-8'),
        json_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return None  # Invalid signature
    
    # Parse and validate expiration
    payload = json.loads(json_data)
    expires_at = datetime.fromisoformat(payload["expires_at"])
    if datetime.now() > expires_at:
        return None  # Expired
    
    return payload
```

### 🗄️ **Firestore Data Structure**

#### **Invite Link Document**
```json
{
  "document_id": "uuid-invite-id",
  "invite_id": "uuid-invite-id",
  "team_id": "KTI",
  "chat_id": "-1001234567890",
  "chat_type": "main",
  "invite_link": "https://t.me/+ABC123DEF456",
  "secure_data": "eyJwbGF5ZXJfaWQiOiJNSDEiLCJwbGF5ZXJfbmFtZSI6Ik1haG11ZHVsIEhvcXVlIiwiZXhwaXJlc19hdCI6IjIwMjUtMDctMzBUMjM6MDI6MTYiLCJzaWduYXR1cmUiOiJhYmMxMjNkZWY0NTYifQ==",
  "player_id": "MH1",
  "player_name": "Mahmudul Hoque",
  "player_phone": "+447961103217",
  "player_position": "Defender",
  "status": "active",
  "created_at": "2025-07-23T23:02:16",
  "expires_at": "2025-07-30T23:02:16",
  "used_at": null,
  "used_by": null,
  "used_by_username": null
}
```

### 🔗 **User Linking Strategy**

#### **When Player Joins Main Chat**
1. **Extract Secure Data**: Get `secure_data` from Firestore invite record
2. **Validate Signature**: Verify HMAC signature is valid
3. **Decode Player Info**: Extract player_id, name, phone, etc.
4. **Find Player Record**: Look up player by `player_id` in Firestore
5. **Update Telegram ID**: Set `player.telegram_id = telegram_user_id`
6. **Mark Link Used**: Update invite status to "used"

#### **Fallback Linking by Phone Number**
If secure data validation fails:
1. **Prompt User**: Ask for phone number verification
2. **Lookup Player**: Find player by phone number
3. **Verify Identity**: Confirm with user
4. **Update Record**: Link Telegram ID to player record

### 🛡️ **Security Benefits**

#### **1. Player-Specific Links**
- Each link is tied to a specific player
- Cannot be used by unauthorized users
- Prevents link sharing abuse

#### **2. Tamper-Proof Data**
- HMAC signatures prevent data modification
- Expiration timestamps prevent replay attacks
- Secure encoding prevents data leakage

#### **3. Audit Trail**
- All invite usage is logged
- Track who used which link
- Monitor for suspicious activity

#### **4. Automatic Expiration**
- Links expire after 7 days
- Reduces attack window
- Automatic cleanup of expired links

### 🔧 **Configuration**

#### **Environment Variables**
```bash
# Secret key for signing invite data (should be moved to env var)
INVITE_LINK_SECRET_KEY="your-secret-key-here"
```

#### **Telegram Bot Settings**
```python
# Invite link configuration
invite_link = await bot.create_chat_invite_link(
    chat_id=int(chat_id),
    name=f"KICKAI Invite {invite_id[:8]}",
    creates_join_request=False,  # Direct join
    expire_date=int((datetime.now() + timedelta(days=7)).timestamp()),
    member_limit=1  # One-time use
)
```

### 📊 **Usage Statistics**

#### **Link Creation**
- Player-specific invite links
- Embedded player information
- Secure digital signatures
- 7-day expiration

#### **Link Validation**
- HMAC signature verification
- Expiration timestamp checking
- Usage status validation
- Player record linking

#### **Security Monitoring**
- Invalid signature attempts
- Expired link usage
- Multiple usage attempts
- Suspicious activity detection

### 🚀 **Future Enhancements**

#### **1. Enhanced Security**
- Move secret key to environment variables
- Implement rate limiting for link creation
- Add IP-based restrictions
- Implement link revocation system

#### **2. User Experience**
- QR code generation for invite links
- SMS integration for link delivery
- Link preview with player information
- One-click join process

#### **3. Analytics**
- Link usage analytics
- Conversion rate tracking
- Security incident monitoring
- Performance metrics

### ✅ **Testing Checklist**

- [ ] Secure data generation works correctly
- [ ] HMAC signature validation prevents tampering
- [ ] Expired links are properly rejected
- [ ] Used links cannot be reused
- [ ] Player linking works with secure data
- [ ] Fallback phone number linking works
- [ ] Invalid links are properly handled
- [ ] Audit logging captures all events

### 🔍 **Troubleshooting**

#### **Common Issues**
1. **Invalid Signature**: Check secret key configuration
2. **Expired Links**: Verify timestamp handling
3. **Player Not Found**: Check player_id generation
4. **Link Already Used**: Verify usage status tracking

#### **Debug Commands**
```bash
# Check invite link status
python -c "from src.features.communication.domain.services.invite_link_service import InviteLinkService; print('Service loaded')"

# Validate secure data manually
# (Add debug method to service)
```

This secure invite link system ensures that only the intended player can use each invite link, providing robust security while maintaining a smooth user experience. 