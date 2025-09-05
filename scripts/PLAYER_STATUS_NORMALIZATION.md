# Player Status Normalization

## Problem
The `list_players_active` tool is returning zero active players because of inconsistent status field naming in Firestore:
- Some records use `status` field (older player records)
- Some records use `onboarding_status` field (newer team member records)

## Solution
This normalization script standardizes all player records to use the `status` field.

## Usage

### 1. Preview Changes (Recommended First)
```bash
cd /Users/mahmud/projects/KICKAI
./scripts/run_player_status_normalization.sh --dry-run
```

### 2. Verify Current Status
```bash
./scripts/run_player_status_normalization.sh --verify
```

### 3. Apply Normalization
```bash
./scripts/run_player_status_normalization.sh
```

## What the Script Does

1. **Finds** all documents with `onboarding_status` field
2. **Copies** the value to `status` field
3. **Removes** the `onboarding_status` field
4. **Updates** the `updated_at` timestamp
5. **Reports** statistics on the changes made

## Collections Processed

- `kickai_KTI_players` - Main players collection
- `kickai_KTI_team_members` - Team members who may also be players

## Status Value Mapping

The script preserves the exact status values:
- `"active"` → `"active"`
- `"pending"` → `"pending"`
- `"approved"` → `"approved"`
- etc.

## Safety Features

- **Dry Run Mode**: Preview all changes before applying
- **Verification Mode**: Check current database state
- **Error Handling**: Continues processing even if individual documents fail
- **Detailed Logging**: Full audit trail of all changes
- **Rollback Friendly**: Changes are additive (adds `status` field) before removing `onboarding_status`

## Expected Results

After running the normalization:
- All player records will have a consistent `status` field
- No records will have `onboarding_status` field
- The `list_players_active` tool will correctly find all active players

## Troubleshooting

If the script fails:
1. Check that the virtual environment is activated: `source venv311/bin/activate`
2. Verify environment variables: `export PYTHONPATH=. && export KICKAI_INVITE_SECRET_KEY=test-key`
3. Check Firebase credentials are configured correctly
4. Run in `--verify` mode to check current database state

## Manual Verification

After normalization, you can verify the fix by running:
```bash
# Test the tool that was failing
make dev
# In Telegram or Mock UI, try: "list all players"
```

The command should now return the active players instead of "No active players found".