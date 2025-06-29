import os
import subprocess
import json

# List of required Firebase variables
REQUIRED_VARS = [
    "FIREBASE_PROJECT_ID",
    "FIREBASE_PRIVATE_KEY",
    "FIREBASE_CLIENT_EMAIL",
    "FIREBASE_CLIENT_ID",
    "FIREBASE_AUTH_URI",
    "FIREBASE_TOKEN_URI",
    "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
    "FIREBASE_CLIENT_X509_CERT_URL"
]

def get_railway_env():
    # Get Railway environment variables as JSON
    result = subprocess.run(["railway", "variables", "--json"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Failed to fetch Railway variables. Are you linked to the right project?")
        print(result.stderr)
        exit(1)
    return json.loads(result.stdout)

def check_firebase_vars(env_vars):
    missing = []
    for var in REQUIRED_VARS:
        value = env_vars.get(var)
        if not value or value.strip() == "":
            missing.append(var)
        elif var == "FIREBASE_PRIVATE_KEY" and "PRIVATE KEY" not in value:
            print(f"⚠️ {var} does not look like a private key!")
    if missing:
        print("❌ Missing Firebase variables:", ", ".join(missing))
    else:
        print("✅ All required Firebase variables are present and non-empty.")

def main():
    env_vars = get_railway_env()  # Already a dict
    check_firebase_vars(env_vars)
    print("\nIf you need to set or fix a variable, use:")
    print("  railway variables set VARIABLE_NAME 'value'")

if __name__ == "__main__":
    main() 