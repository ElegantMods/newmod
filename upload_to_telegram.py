import os
import json
import glob
import time
import math
import logging
import subprocess
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.types import (
    InputMediaUploadedDocument,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
)

logging.basicConfig(level=logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)

# --- Inputs come from environment variables / GitHub Actions secrets ---
video_url = os.environ["VIDEO_URL"]
api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]
session_string = os.environ["TELEGRAM_SESSION"]

_raw_qualities = os.environ.get("QUALITIES", "1080")
qualities = []
for part in _raw_qualities.split(","):
    part = part.strip()
    if not part:
        continue
    q = int(part)
    if q <= 0:
        raise ValueError(f"Quality '{q}' must be a positive number.")
    qualities.append(q)
if not qualities:
    raise ValueError("No valid qualities provided in QUALITIES.")
qualities = sorted(set(qualities))

# Set MAX_SIZE_GB env var to "3.9" if you have Telegram Premium, else leave default 1.9
MAX_SIZE_BYTES = float(os.environ.get("MAX_SIZE_GB", "1.9")) * 1024 * 1024 * 1024

# Optional path to a cookies.txt file (Netscape format) to help the
# downloader access videos that require a signed-in session.
cookies_file = os.environ.get("WEB_COOKIES_FILE", "")
DOWNLOADER_EXTRA_ARGS = ""
if cookies_file and os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 0:
    DOWNLOADER_EXTRA_ARGS += f' --cookies "{cookies_file}"'
DOWNLOADER_EXTRA_ARGS += " --js-runtimes deno --remote-components ejs:github"


def download_video_thumbnail(url, extra_args=""):
    # Uses yt-dlp's own thumbnail downloader, which works across whichever
    # site yt-dlp is downloading from, rather than assuming a specific site's
    # URL layout.
    try:
        for f in glob.glob("thumb.*"):
            os.remove(f)
        cmd = (
            f'yt-dlp -q --write-thumbnail --skip-download {extra_args} '
            f'-o "thumb.%(ext)s" "{url}"'
        )
        subprocess.run(cmd, shell=True)
        found = glob.glob("thumb.*")
        return found[0] if found else None
    except Exception:
        return None


def get_video_meta(file_path):
    try:
        cmd = (
            f'ffprobe -v error -print_format json -show_entries stream=width,height '
            f'-show_entries format=duration "{file_path}"'
        )
        meta = json.loads(subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout)
        duration = int(float(meta["format"]["duration"]))
        width = meta["streams"][0]["width"]
        height = meta["streams"][0]["height"]
        return duration, width, height
    except Exception:
        return 0, 1280, 720


def split_video(file_path):
    file_size = os.path.getsize(file_path)
    num_parts = math.ceil(file_size / MAX_SIZE_BYTES)
    duration_result = subprocess.run(
        f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"',
        shell=True, capture_output=True, text=True,
    )
    try:
        total_duration = float(duration_result.stdout.strip())
    except Exception:
        return [file_path]

    part_duration = total_duration / num_parts
    base_name, ext = os.path.splitext(file_path)
    split_files = []

    print(f"\nSplitting into {num_parts} part(s)...")
    for i in range(num_parts):
        start_time = i * part_duration
        out_part_name = f"{base_name}_Part{i + 1}{ext}"
        cmd = f'ffmpeg -y -v quiet -ss {start_time} -i "{file_path}" -t {part_duration} -c copy "{out_part_name}"'
        subprocess.run(cmd, shell=True)
        if os.path.exists(out_part_name):
            split_files.append(out_part_name)

    os.remove(file_path)
    return split_files


def create_progress_bar(file_name, mode):
    def progress_callback(current, total):
        percentage = (current / total) * 100
        print(
            f"[{mode}] {file_name}: {percentage:.2f}% "
            f"({current / (1024**2):.1f}MB / {total / (1024**2):.1f}MB)"
        )

    return progress_callback


async def main():
    thumb_path = download_video_thumbnail(video_url, DOWNLOADER_EXTRA_ARGS)

    print("Connecting to Telegram...")
    async with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        print("Connected.")

        print(f"\nDownloading qualities {qualities} and preparing album upload...")
        album_files = []
        for q in qualities:
            out_template = f"%(title)s_{q}p.mp4"
            format_str = f"bestvideo[height<={q}]+bestaudio/best[height<={q}]"
            os.system(
                f'yt-dlp -q --progress -f "{format_str}" --merge-output-format mp4 '
                f'{DOWNLOADER_EXTRA_ARGS} -o "{out_template}" "{video_url}"'
            )

            found = glob.glob(f"*_{q}p.mp4")
            if found:
                file_path = found[0]
                if os.path.getsize(file_path) > MAX_SIZE_BYTES:
                    album_files.extend(split_video(file_path))
                else:
                    album_files.append(file_path)

        album_media = []
        if album_files:
            uploaded_thumb = await client.upload_file(thumb_path) if thumb_path else None

            for idx, file_path in enumerate(album_files, start=1):
                raw_name = os.path.basename(file_path)
                print(f"Uploading: {raw_name}")

                uploaded_file = await client.upload_file(
                    file_path,
                    progress_callback=create_progress_bar(raw_name, f"part {idx}/{len(album_files)}"),
                )

                file_name_attribute = DocumentAttributeFilename(file_name=raw_name)
                media_doc = InputMediaUploadedDocument(
                    file=uploaded_file,
                    mime_type="video/mp4",
                    attributes=[file_name_attribute],
                    thumb=uploaded_thumb,
                )
                album_media.append(media_doc)
                time.sleep(3)

            print("\nSending album to Saved Messages...")
            await client.send_file("me", album_media)

            for f in album_files:
                try:
                    os.remove(f)
                except Exception:
                    pass
            print("Done.")
        else:
            print("No video file was downloaded — check the URL and yt-dlp output above.")

        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
