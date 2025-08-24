# Security Environment Variables

## Required Environment Variables

The KICKAI application requires the following environment variables to be set for secure operation:

### Bot Tokens
- `KICKAI_TESTING_BOT_TOKEN`: Testing bot token for seeding database mappings
  - **NEVER** hardcode this token in source code
  - Must be provided when running `seed_kickai_testing_bot_mapping()`

### API Keys
- `HUGGINGFACE_API_TOKEN`: For Hugging Face LLM provider (optional)
- `GROQ_API_KEY`: For Groq LLM provider (optional)
- `OPENAI_API_KEY`: For OpenAI LLM provider (optional)

### Other Secrets
- `KICKAI_INVITE_SECRET_KEY`: Used for generating secure invite links

## Security Guidelines

1. **Never commit secrets to version control**
2. **Use environment variables for all secrets**
3. **Use `.env` files for local development** (not committed)
4. **Use secure secret management in production**

## Example .env file

```bash
# Bot Configuration
KICKAI_TESTING_BOT_TOKEN=your_bot_token_here

# LLM Provider API Keys (choose one or more)
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_TOKEN=your_hf_token_here

# Application Secrets
KICKAI_INVITE_SECRET_KEY=your_invite_secret_here

# Database Configuration  
FIREBASE_PROJECT_ID=your_firebase_project_id
```

## Security Incident Response

If any secrets are accidentally committed:
1. **Immediately rotate the compromised secrets**
2. **Remove from git history using `git filter-branch` or BFG**
3. **Update all deployment environments**
4. **Review access logs for potential unauthorized usage**

## Code Review Checklist

- [ ] No hardcoded secrets in source code
- [ ] All secrets loaded via environment variables
- [ ] Environment variables validated at startup
- [ ] Error messages don't expose secrets
- [ ] Secrets not logged or included in debug output