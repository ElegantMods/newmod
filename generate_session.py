"""
Run this ONCE on your own computer (not in GitHub Actions).
It logs you into Telegram interactively (asks for phone + code, and your
2FA password if you have one), then prints a SESSION STRING.

That string is the fix for the "asks for phone number" problem: paste it
into a GitHub secret (TELEGRAM_SESSION) and the Actions workflow will use
it to log in silently, with zero prompts, forever (until you revoke it).

Requirements:
    pip install telethon

Usage:
    python generate_session.py
"""

from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(input("Enter your api_id: ").strip())
API_HASH = input("Enter your api_hash: ").strip()

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    session_string = client.session.save()

    # Write to a file so there's no error-prone copy/paste from the terminal.
    with open("session.txt", "w", newline="") as f:
        f.write(session_string)

    print("\nSession string saved to session.txt in the current folder.")
    print("Open that file, select-all, copy, and paste the ENTIRE contents")
    print("(no extra spaces or newlines) into the TELEGRAM_SESSION GitHub secret.")
    print("\nTreat this string like a password — anyone who has it can")
    print("access your Telegram account without your phone or 2FA.")
    print("Delete session.txt once you've saved it to GitHub.")
