# Web Video to Telegram Uploader (GitHub Actions)

[نسخه فارسی](https://github.com/ElegantMods/newmod/blob/main/README.FA.MD)

This repository downloads an online video at whatever quality (or qualities)
you choose, and uploads it to your own Telegram account's "Saved Messages" --
all running automatically on GitHub's servers, so your own computer does not
need to stay on or do any of the work.

You trigger it manually from the GitHub website each time you want to grab a
video. No coding knowledge is required to use it day to day. The one-time
setup below does require creating a couple of accounts and copying some
values around, but every step is explained in plain language.

## What you need before you start

- A GitHub account that is **not** your main personal account. Use a
  secondary or throwaway account for this, since the repository will be
  running automated downloads on your behalf and it's best to keep that
  separate from your primary identity on GitHub.
- A Telegram account.
- A web browser where you can log into the video site you plan to use.
- About 15 minutes for the one-time setup. After that, running it takes one click.

## How it works, in plain terms

1. You click "Run workflow" on GitHub and type in a video link, the
   quality (or qualities) you want, and whether you have Telegram Premium.
2. GitHub spins up a temporary computer, downloads the video with a
   general-purpose downloading tool, and logs into your Telegram account
   using credentials you set up once in advance.
3. The video is uploaded to your own "Saved Messages" chat in Telegram, with
   its thumbnail attached where available so it looks and plays like a
   normal video.
4. The temporary computer is destroyed afterward. Nothing is kept on GitHub's
   side between runs.

Your Telegram login details and browser cookies are stored as encrypted
"secrets" in your GitHub repository settings. They are never shown in logs
and only used inside your own automated runs.

---

## One-time setup

### Step 1: Fork this repository into your own account

1. Make sure you are signed into GitHub with the secondary account
   mentioned above, not your main personal account.
2. On this repository's GitHub page, click the **Fork** button (top right
   of the page).
3. Choose your account as the destination and click **Create fork**. This
   creates your own copy of the repository under your account. Note that
   a fork is public by default unless the original repository is private
   or your GitHub plan allows private forks -- if you want your fork to be
   private, check GitHub's current documentation on making a fork private,
   since this is not something this repository's setup controls.
4. Do all of the remaining steps, and all future runs, inside your forked
   copy -- not the original repository.

Forking (rather than just copying the files by hand) keeps your copy
properly connected to GitHub Actions and makes it easy to pull in any future
updates from the original repository if you want them. You need to be the
owner of the fork so you can add secrets to it in Step 5.

### Step 2: Get a Telegram API ID and API hash

Telegram requires every application that logs in on your behalf to register
for an "API ID" and "API hash". This is free and only takes a minute.

1. Go to <https://my.telegram.org/apps> in your browser.
2. Log in with your Telegram phone number (Telegram will send you a login
   code in the Telegram app).
3. Fill in the "Create new application" form. You can put anything for
   "App title" and "Short name", for example "my-uploader". Leave the other
   fields blank.
4. After submitting, you will see a page with **App api_id** (a number) and
   **App api_hash** (a long string of letters and numbers). Keep this page
   open or copy both values somewhere safe. You will need them again in
   Step 5.

### Step 3: Generate a Telegram "session string"

Because this tool logs into your real Telegram account (not a bot), Telegram
normally asks for your phone number and a login code the first time. We do
this once, on your own computer, and save the result as a "session string"
so that GitHub Actions never needs to ask for your phone number again.

1. Make sure Python is installed on your computer. If you are not sure,
   open a terminal (Command Prompt, PowerShell, or Terminal) and type
   `python --version`. If you see a version number, you have Python.
   If not, download it from <https://www.python.org/downloads/>.
2. In a terminal, install the required library:

   ```
   pip install telethon
   ```

3. Download the `generate_session.py` file from this repository to your
   computer (or copy its contents into a new file with that name).
4. Run it:

   ```
   python generate_session.py
   ```

5. It will ask for your `api_id` and `api_hash` from Step 2, then your
   Telegram phone number, then the login code Telegram sends you, and your
   two-step-verification password if you have one set up.
6. Once logged in, the script creates a file called `session.txt` in the
   same folder. Open that file, select all of its contents, and copy them.
   This text is your session string. Keep it as private as a password --
   anyone who has it can access your Telegram account.
7. Delete `session.txt` from your computer once you have copied it into
   GitHub in Step 5, since you no longer need to keep a local copy.

### Step 4: Export your browser cookies

Many video sites limit or block automated downloads from data-center
computers (which is what GitHub Actions uses). The reliable workaround is to
give the downloader a copy of your browser's login cookies for that site, so
it looks like a normal signed-in visit rather than an anonymous automated
request.

It is recommended to use a secondary or throwaway account for this, rather
than your main personal account, since this account's cookies will be used
repeatedly from GitHub's servers.

1. In Chrome, Firefox, or Edge, install a cookie-export extension such as
   "Get cookies.txt LOCALLY" from your browser's extension store.
2. Log into the video site normally in that browser, with the account you
   want to use.
3. While on that site, click the extension's icon and choose the option to
   export cookies for the current site. Save the file -- it will usually be
   named `cookies.txt` or similar.
4. Open the downloaded file in a text editor, select all of its contents,
   and copy them. You will paste this into GitHub in the next step.

Cookies can expire or stop working after a while (for example, if you log
out of that browser session). If the workflow starts failing again with a
message about signing in or confirming you are not a bot, simply repeat this
step to get a fresh cookies file and update the secret in Step 5.

### Step 5: Add your secrets to GitHub

"Secrets" are private values that GitHub stores encrypted and only makes
available inside your own workflow runs. They are never visible in logs or
to anyone browsing your repository.

1. Open your repository on GitHub.
2. Click **Settings** (top menu of the repository, not your account
   settings).
3. In the left sidebar, click **Secrets and variables**, then **Actions**.
4. Click **New repository secret** and add each of the following one at a
   time (exact name on the left, your own value on the right):

   | Secret name | Value |
   |---|---|
   | `TELEGRAM_API_ID` | The api_id number from Step 2 |
   | `TELEGRAM_API_HASH` | The api_hash string from Step 2 |
   | `TELEGRAM_SESSION` | The full session string from Step 3 |
   | `WEB_COOKIES` | The full contents of the cookies file from Step 4 |

   When pasting `TELEGRAM_SESSION` and `WEB_COOKIES`, paste only the exact
   text with nothing added before or after it (no extra blank lines, no
   quotation marks).

That's it. Setup is complete and you will not need to repeat these steps
unless your cookies expire (Step 4) or you want to use a different Telegram
or site account.

---

## Running it (every time you want a video)

1. Open your repository on GitHub.
2. Click the **Actions** tab near the top of the page.
3. In the left sidebar, click **Download Web Video to Telegram**.
4. Click the **Run workflow** button (usually on the right side, may need a
   dropdown click first).
5. Fill in the fields:
   - **Video URL**: paste the full link to the video.
   - **Qualities**: type one quality or several separated by commas, for
     example `1080`, or `480,1080`, or `360,480,720,1080,2160`. Each
     quality you list will be downloaded and sent as a separate file in the
     same batch. If a video does not have the exact quality you ask for,
     the closest available quality at or below your request is used
     automatically.
   - **Do you have Telegram Premium?**: choose "yes" or "no". Telegram
     limits how large a single file can be; Premium accounts can receive
     larger files (up to about 3.9 GB) while regular accounts are limited to
     about 1.9 GB. If a downloaded video is larger than this limit, it is
     automatically split into smaller parts before uploading, so you will
     always receive the full video either as one file or as several parts.
6. Click the green **Run workflow** button to start.
7. Click into the run that appears (it will have a spinning yellow icon
   while in progress) to watch its progress, or just wait -- when finished,
   open Telegram and check your **Saved Messages** chat.

Depending on the video's length and how many qualities you chose, this can
take anywhere from a couple of minutes to a while for very long videos. You
can watch the live log by clicking into the running workflow and then into
the "Run uploader" step.

## Troubleshooting

**A message about signing in or confirming you're not a bot appears in the log.**
Your browser cookies (Step 4) have likely expired. Log into the video site
again in your browser, re-export the cookies file, and update the
`WEB_COOKIES` secret in your repository settings with the new contents.

**The Telegram connection step fails with an error about the session.**
Your session string may have been pasted incorrectly (for example, with
extra spaces or a missing character). Repeat Step 3 to generate a fresh
session string and replace the `TELEGRAM_SESSION` secret with the new value,
making sure to copy the entire contents of `session.txt` exactly.

**"No video file was downloaded" appears at the end.**
Scroll up in the log to see the actual error from the downloader above that
message. Common causes are an incorrect or private video URL, expired
cookies (see above), or the video being unavailable in your account's
region.

**Nothing appears in Saved Messages even though the run succeeded.**
Make sure you are checking the same Telegram account whose phone number you
used in Step 3 when generating the session string.

## Notes on privacy and safety

- Your Telegram session string and browser cookies grant access to those
  accounts. Only store them as GitHub secrets (as instructed above) and
  never paste them into a public place, an issue, a chat message, or share
  the repository with people you do not trust, since collaborators with
  write access to the repository's settings could otherwise access the same
  secrets.
- Only download and redistribute videos you have the rights to, or that are
  otherwise permitted for personal use under the source site's terms and
  applicable copyright law.
- Each run is disconnected and temporary. GitHub does not retain the
  downloaded video files after a run finishes.
