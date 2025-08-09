# Rate Limiting Implementation for KICKAI

## Overview

This document describes the rate limiting implementation for the KICKAI system, specifically designed to handle Groq's free tier rate limits and other AI provider limitations.

## Problem Statement

The system was experiencing rate limit errors from Groq:
```
RateLimitError: GroqException - {"error":{"message":"Rate limit reached for model `llama3-8b-8192` in organization `org_01k1zerdxqfrgt7nxpccyfrmzk` service tier `on_demand` on tokens per minute (TPM): Limit 6000, Used 4673, Requested 1733. Please try again in 4.052s.
```

## Solution Architecture

### 1. Configuration-Based Rate Limiting

**File**: `kickai/core/config.py`

Added rate limiting settings to the configuration system:

```python
# Rate Limiting Configuration
ai_rate_limit_tpm: int = Field(
    default=6000,
    alias="AI_RATE_LIMIT_TPM",
    description="Tokens per minute rate limit (Groq free tier: 6000)"
)
ai_rate_limit_retry_delay: float = Field(
    default=5.0,
    alias="AI_RATE_LIMIT_RETRY_DELAY",
    description="Delay in seconds when rate limit is hit"
)
ai_rate_limit_max_retries: int = Field(
    default=3,
    alias="AI_RATE_LIMIT_MAX_RETRIES",
    description="Maximum retries for rate limit errors"
)
ai_rate_limit_backoff_multiplier: float = Field(
    default=2.0,
    alias="AI_RATE_LIMIT_BACKOFF_MULTIPLIER",
    description="Backoff multiplier for rate limit retries"
)
```

### 2. Rate-Limited LLM Factory

**File**: `kickai/utils/llm_factory_simple.py`

Replaced `SimpleLLMFactory` with `RateLimitedLLMFactory` that includes:

- **Automatic retry logic** for rate limit errors
- **Exponential backoff** with configurable multiplier
- **Error detection** for rate limit vs other errors
- **Logging** of retry attempts and delays

#### Key Features:

```python
def groq_llm_with_retry(messages, **kwargs):
    max_retries = settings.ai_rate_limit_max_retries
    base_delay = settings.ai_rate_limit_retry_delay
    backoff_multiplier = settings.ai_rate_limit_backoff_multiplier
    
    for attempt in range(max_retries + 1):
        try:
            response = completion(...)
            return response.choices[0].message.content
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check if it's a rate limit error
            if "rate limit" in error_str or "rate_limit" in error_str or "tpm" in error_str:
                if attempt < max_retries:
                    delay = base_delay * (backoff_multiplier ** attempt)
                    logger.warning(f"⚠️ Groq rate limit hit (attempt {attempt + 1}/{max_retries + 1}). Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    raise RuntimeError(f"Groq rate limit exceeded after {max_retries + 1} attempts: {e}")
            else:
                # Non-rate-limit error, don't retry
                raise RuntimeError(f"Groq LLM request failed: {e}")
```

### 3. Environment Configuration

**File**: `env.example`

Added rate limiting configuration section:

```bash
# ============================================================================
# RATE LIMITING CONFIGURATION (Groq Free Tier)
# ============================================================================
# Tokens per minute rate limit (Groq free tier: 6000)
AI_RATE_LIMIT_TPM=6000

# Delay in seconds when rate limit is hit
AI_RATE_LIMIT_RETRY_DELAY=5.0

# Maximum retries for rate limit errors
AI_RATE_LIMIT_MAX_RETRIES=3

# Backoff multiplier for rate limit retries
AI_RATE_LIMIT_BACKOFF_MULTIPLIER=2.0
```

## Groq Free Tier Limits

### Current Limits:
- **TPM (Tokens Per Minute)**: 6,000 tokens
- **Concurrent Requests**: Limited
- **Rate Limit Response**: 4-5 second wait time

### Recommended Settings:
- **AI_RATE_LIMIT_TPM**: 6000 (matches Groq free tier)
- **AI_RATE_LIMIT_RETRY_DELAY**: 5.0s (slightly longer than Groq's suggested wait)
- **AI_RATE_LIMIT_MAX_RETRIES**: 3 (reasonable retry limit)
- **AI_RATE_LIMIT_BACKOFF_MULTIPLIER**: 2.0 (exponential backoff)

## Usage

### 1. Environment Setup

Copy the rate limiting settings to your `.env` file:

```bash
# Rate Limiting Configuration
AI_RATE_LIMIT_TPM=6000
AI_RATE_LIMIT_RETRY_DELAY=5.0
AI_RATE_LIMIT_MAX_RETRIES=3
AI_RATE_LIMIT_BACKOFF_MULTIPLIER=2.0
```

### 2. Using Rate-Limited LLM

The system automatically uses rate limiting when creating LLMs:

```python
from kickai.utils.llm_factory_simple import RateLimitedLLMFactory

# Create rate-limited LLM
llm = RateLimitedLLMFactory.create_llm()

# Use normally - rate limiting is automatic
response = llm.invoke([{"role": "user", "content": "Hello"}])
```

### 3. Testing Rate Limiting

Run the test script to verify rate limiting works:

```bash
python scripts/test_rate_limiting.py
```

## Error Handling

### Rate Limit Detection

The system detects rate limit errors by checking for keywords in the error message:
- `"rate limit"`
- `"rate_limit"`
- `"tpm"`

### Retry Strategy

1. **First attempt**: Immediate request
2. **Rate limit hit**: Wait 5 seconds
3. **Second attempt**: Wait 10 seconds (5 × 2.0)
4. **Third attempt**: Wait 20 seconds (5 × 2.0²)
5. **Final failure**: Raise exception after 3 retries

### Logging

The system logs rate limit events:

```
⚠️ Groq rate limit hit (attempt 1/3). Waiting 5.0s...
⚠️ Groq rate limit hit (attempt 2/3). Waiting 10.0s...
❌ Groq rate limit exceeded after 3 attempts
```

## Benefits

1. **Automatic Recovery**: System automatically retries on rate limits
2. **Configurable**: All settings can be adjusted via environment variables
3. **Exponential Backoff**: Prevents overwhelming the API
4. **Error Differentiation**: Only retries rate limit errors, not other errors
5. **Logging**: Clear visibility into rate limit events
6. **Groq Compliance**: Respects Groq's free tier limits

## Future Enhancements

1. **Token Counting**: Track actual token usage to prevent rate limits
2. **Queue System**: Queue requests when approaching limits
3. **Multiple Providers**: Fallback to other providers when rate limited
4. **Metrics**: Track rate limit frequency and response times
5. **Dynamic Adjustment**: Automatically adjust settings based on usage patterns

## Troubleshooting

### Common Issues

1. **Still hitting rate limits**: Increase `AI_RATE_LIMIT_RETRY_DELAY`
2. **Too many retries**: Decrease `AI_RATE_LIMIT_MAX_RETRIES`
3. **Slow responses**: Decrease `AI_RATE_LIMIT_BACKOFF_MULTIPLIER`

### Monitoring

Check logs for rate limit events:
```bash
grep "rate limit" logs/kickai.log
```

### Testing

Use the test script to verify configuration:
```bash
python scripts/test_rate_limiting.py
```
