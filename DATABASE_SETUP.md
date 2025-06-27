# KICKAI Database Setup Guide

This guide explains how to set up the KICKAI database from scratch using the consolidated schema files.

## 📋 Overview

KICKAI uses a comprehensive multi-team database schema that supports:
- Multiple teams with their own bots and chat groups
- Player management with roles and permissions
- Fixture scheduling and availability tracking
- Task management and equipment tracking
- Peer-to-peer ratings and payment tracking

## 🗄️ Database Files

### Core Schema Files
- **`kickai_schema.sql`** - Complete database schema (tables, indexes, constraints)
- **`kickai_sample_data.sql`** - Realistic sample data for testing

### Management Scripts
- **`manage_team_bots.py`** - CLI for managing team-to-bot mappings

## 🚀 Setup Process

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and anon key

### 2. Run Schema Setup
1. Go to your Supabase dashboard → SQL Editor
2. Copy and paste the contents of `kickai_schema.sql`
3. Execute the script
4. This creates all tables, indexes, and constraints

### 3. Add Sample Data (Optional)
1. In the same SQL Editor
2. Copy and paste the contents of `kickai_sample_data.sql`
3. Execute the script
4. This adds a sample team (BP Hatters) with 15 players, fixtures, tasks, etc.

### 4. Configure Bot Mappings
```bash
# List current mappings
python manage_team_bots.py list

# Add your team's bot mapping
python manage_team_bots.py add --team "Your Team Name" --token "your_bot_token" --chat-id "your_chat_id" --username "@your_bot_username"

# Test the mapping
python manage_team_bots.py test --team "Your Team Name"
```

## 📊 Database Schema

### Core Tables
| Table | Purpose | Key Features |
|-------|---------|--------------|
| `teams` | Team information | Name, description, telegram group |
| `team_members` | Team membership | Roles (admin, captain, player), permissions |
| `players` | Player profiles | Name, phone, team association |
| `fixtures` | Match scheduling | Opponent, date, venue, status |
| `availability` | Player availability | Status, payments, fines |
| `squad_selections` | Match squads | Selected players per fixture |
| `ratings` | Player ratings | Peer-to-peer ratings (1-10) |
| `tasks` | Team tasks | Recurring chores and responsibilities |
| `task_assignments` | Task assignments | Who does what for each fixture |
| `equipment` | Team equipment | Inventory tracking |
| `team_bots` | Bot mappings | Telegram bot tokens per team |

### Key Relationships
- Teams have many members, fixtures, tasks, and equipment
- Players belong to teams and have availability for fixtures
- Team members have roles and permissions
- Fixtures have squad selections and task assignments
- All tables use UUID primary keys for scalability

## 🔧 Management Commands

### Bot Mapping Management
```bash
# List all teams and their bot mappings
python manage_team_bots.py list

# Add a new bot mapping
python manage_team_bots.py add --team "Team Name" --token "bot_token" --chat-id "chat_id" --username "@bot_username"

# Remove a bot mapping
python manage_team_bots.py remove --team "Team Name"

# Test a bot mapping
python manage_team_bots.py test --team "Team Name"
```

### Database Verification
```bash
# Test database connection and schema
python test_database_setup.py

# Test team management
python test_team_setup.py

# Test sample data
python test_sample_data.py
```

## 🧹 Cleanup

The following old files have been removed and consolidated:
- ❌ `setup_multi_team_schema.sql` → ✅ `kickai_schema.sql`
- ❌ `setup_telegram_bot_mapping.sql` → ✅ `kickai_schema.sql`
- ❌ `create_team_bots_table.sql` → ✅ `kickai_schema.sql`
- ❌ `check_bot_mapping.py` → ✅ `manage_team_bots.py`
- ❌ `setup_bp_hatters_mapping.py` → ✅ `manage_team_bots.py`
- ❌ `setup_bot_mapping.py` → ✅ `manage_team_bots.py`
- ❌ `create_team_bots_table.py` → ✅ `manage_team_bots.py`

## 🚨 Troubleshooting

### Common Issues

1. **Foreign Key Constraint Errors**
   - Ensure you run `kickai_schema.sql` before `kickai_sample_data.sql`
   - Check that all referenced tables exist

2. **Bot Mapping Errors**
   - Verify team name exists in database
   - Check bot token and chat ID format
   - Ensure bot has admin permissions in Telegram group

3. **Connection Issues**
   - Verify SUPABASE_URL and SUPABASE_KEY in .env
   - Check network connectivity
   - Ensure Supabase project is active

### Verification Commands
```bash
# Test database connection
python -c "from src.tools.supabase_tools import get_supabase_client; print('✅ Connected')"

# List all tables
python -c "from src.tools.supabase_tools import get_supabase_client; client = get_supabase_client(); print('Tables:', [t for t in client.table('teams').select('*').limit(1).execute()])"
```

## 📈 Next Steps

After setting up the database:
1. Configure your Telegram bot (see `TELEGRAM_SETUP_GUIDE.md`)
2. Test the system with `python test_telegram_features.py`
3. Test AI agents with `python test_crewai_ollama_correct.py`
4. Start using the system for your team management!

---

For more information, see the main [README.md](README.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md). 