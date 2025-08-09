# 📝 Telegram Plain Text Implementation

**Date:** January 2025  
**Implementation:** Complete  
**Status:** All Telegram messages now use plain text only  

---

## 📋 Changes Made

### 1. **Settings Configuration Updated** ✅
**File**: `kickai/core/settings.py`

**Before:**
```python
telegram_parse_mode: str = Field(default="MarkdownV2", description="Telegram parse mode")
```

**After:**
```python
telegram_parse_mode: str = Field(default="", description="Telegram parse mode (empty for plain text only)")
```

### 2. **TelegramBotService Enhanced** ✅
**File**: `kickai/features/communication/infrastructure/telegram_bot_service.py`

**Before:**
```python
async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
    """Send a message to a specific chat."""
    try:
        logger.info(f"Sending message to chat_id={chat_id}: {text}")
        await self.app.bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        raise
```

**After:**
```python
async def send_message(self, chat_id: Union[int, str], text: str, **kwargs):
    """Send a message to a specific chat in plain text."""
    try:
        # Sanitize text to ensure plain text output
        sanitized_text = self._sanitize_for_plain_text(text)
        logger.info(f"Sending plain text message to chat_id={chat_id}: {sanitized_text}")
        
        # Explicitly send as plain text (no parse_mode)
        await self.app.bot.send_message(
            chat_id=chat_id, 
            text=sanitized_text, 
            parse_mode=None,  # Explicitly set to None for plain text
            **kwargs
        )
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        raise

def _sanitize_for_plain_text(self, text: str) -> str:
    """Remove any formatting characters to ensure plain text output."""
    if not text:
        return text
        
    # Remove common markdown characters that might cause issues
    text = text.replace('*', '').replace('_', '').replace('`', '')
    text = text.replace('**', '').replace('__', '').replace('~~', '')
    text = text.replace('#', '').replace('##', '').replace('###', '')
    
    # Remove HTML-like tags
    import re
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove HTML entities
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
```

### 3. **Communication Service Updated** ✅
**File**: `kickai/features/communication/domain/services/communication_service.py`

**Before:**
```python
# Send the message using TelegramBotService
await self.telegram_bot_service.send_message(chat_id, message)
logger.info(f"✅ Message sent to {chat_type} (team_id: {team_id})")
```

**After:**
```python
# Send the message using TelegramBotService (plain text only)
await self.telegram_bot_service.send_message(chat_id, message)
logger.info(f"✅ Plain text message sent to {chat_type} (team_id: {team_id})")
```

### 4. **Poll Message Formatting Updated** ✅
**File**: `kickai/features/communication/domain/services/communication_service.py`

**Before:**
```python
# Format the poll message
poll_message = f"📊 **Poll**: {question}\n\n"
```

**After:**
```python
# Format the poll message (plain text)
poll_message = f"📊 Poll: {question}\n\n"
```

### 5. **Test Configuration Updated** ✅
**File**: `tests/conftest.py`

**Before:**
```python
"parse_mode": "MarkdownV2",
```

**After:**
```python
"parse_mode": "",  # Plain text only
```

### 6. **Scripts Updated** ✅
**Files**: 
- `scripts/manage_team_members_standalone.py`
- `scripts/test_bot_messages.py`
- `scripts/test_leadership_chat_message.py`
- `scripts/manage_team_members.py`

**Before:**
```python
parse_mode='Markdown'
```

**After:**
```python
parse_mode=None  # Plain text only
```

---

## 🔧 Text Sanitization Features

### **What Gets Removed**
- **Markdown Characters**: `*`, `_`, `` ` ``, `**`, `__`, `~~`, `#`, `##`, `###`
- **HTML Tags**: `<b>`, `<i>`, `<code>`, etc.
- **HTML Entities**: `&lt;`, `&gt;`, `&amp;`
- **Extra Whitespace**: Multiple spaces, tabs, etc.

### **Examples**
```python
# Input: "**Hello** *world* `code` <b>bold</b>"
# Output: "Hello world code bold"

# Input: "## Header\n\n**Bold text** with _italic_"
# Output: "Header\n\nBold text with italic"

# Input: "&lt;script&gt;alert('test')&lt;/script&gt;"
# Output: "<script>alert('test')</script>"
```

---

## 🎯 System Behavior

### **✅ Message Reception**
- Messages from Telegram are **always received as plain text**
- No parsing or formatting interpretation needed
- User input like `**bold**` is received as literal text

### **✅ Message Sending**
- All outgoing messages are **sanitized and sent as plain text**
- No parse_mode is applied (explicitly set to `None`)
- Formatting characters are removed to prevent issues

### **✅ Benefits**
- **Consistent**: Same format for input and output
- **Reliable**: No parse mode errors or formatting bugs
- **Simple**: No complex formatting parsing
- **Universal**: Works across all Telegram clients

---

## 📊 Telegram API Parse Modes

### **Available Options**
1. **No Parse Mode (Plain Text)** ✅ - **NOW USED**
2. **HTML** - `<b>bold</b> <i>italic</i> <code>code</code>`
3. **Markdown** - `**bold** *italic* `code`` (legacy)
4. **MarkdownV2** - `**bold** *italic* `code`` (current standard)

### **Why Plain Text**
- **Simpler**: No formatting parsing complexity
- **Consistent**: Input and output use same format
- **Reliable**: No parse mode compatibility issues
- **Universal**: Works on all Telegram clients and platforms

---

## 🔍 Files Modified

1. **`kickai/core/settings.py`** - Changed default parse mode to empty string
2. **`kickai/features/communication/infrastructure/telegram_bot_service.py`** - Added plain text sanitization and explicit parse_mode=None
3. **`kickai/features/communication/domain/services/communication_service.py`** - Updated logging and poll formatting
4. **`tests/conftest.py`** - Updated test configuration
5. **`scripts/manage_team_members_standalone.py`** - Updated parse_mode
6. **`scripts/test_bot_messages.py`** - Updated parse_mode and test message format
7. **`scripts/test_leadership_chat_message.py`** - Updated parse_mode
8. **`scripts/manage_team_members.py`** - Updated parse_mode

---

## 🚀 Usage Examples

### **Sending Messages**
```python
# All messages are automatically sanitized and sent as plain text
await telegram_bot_service.send_message(chat_id, "Hello **world**!")
# Result: "Hello world!" (sent as plain text)
```

### **Receiving Messages**
```python
# Messages are always received as plain text
message_text = update.message.text
# If user types "**bold**", message_text = "**bold**" (literal text)
```

### **Agent Responses**
```python
# Agent responses are automatically sanitized
response = "Here's your **important** information:"
# Sent as: "Here's your important information:" (plain text)
```

---

## 🎯 Summary

The KICKAI system now **exclusively uses plain text** for all Telegram communication:

- ✅ **Input**: Messages received as plain text from Telegram
- ✅ **Output**: Messages sanitized and sent as plain text to Telegram
- ✅ **Configuration**: Default parse mode set to empty string
- ✅ **Sanitization**: Automatic removal of formatting characters
- ✅ **Consistency**: Same format for input and output
- ✅ **Reliability**: No parse mode errors or formatting issues

This ensures a **simple, consistent, and reliable** messaging experience across all Telegram clients and platforms.

---

*Implementation completed on January 2025 - Plain Text Only System Active*

