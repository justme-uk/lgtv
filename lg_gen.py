import json
import sys
import time
import base64
import zlib
from datetime import datetime, timezone

import requests

API_URL = 'https://api.lgchannels.com/api/v1.0/schedulelist'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

REGIONS = {
    'us': {
        'country': 'US',
        'language': 'en',
        'm3u_filename': 'lg_channels_us.m3u',
        'epg_filename': 'lg_channels_us.xml',
    },
    'gb': {
        'country': 'GB',
        'language': 'en-GB',
        'm3u_filename': 'lg_channels_gb.m3u',
        'epg_filename': 'lg_channels_gb.xml',
    },
}

GITHUB_USERNAME = 'justme-uk'
REPO_NAME = 'lgtv'
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5


def build_headers(region):
    return {
        'user-agent': USER_AGENT,
        'x-device-country': region['country'],
        'x-device-language': region['language'],
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://channel-lineup.lgchannels.com/',
        'origin': 'https://channel-lineup.lgchannels.com',
    }


def decode_payload(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    try:
        decoded = base64.b64decode(response_text)
        decompressed = zlib.decompress(decoded)
        return json.loads(decompressed)
    except Exception:
        pass

    try:
        decoded = base64.b64decode(response_text)
        return json.loads(decoded.decode('utf-8'))
    except Exception:
        return None


def fetch_data(region):
    headers = build_headers(region)
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(API_URL, headers=headers, timeout=30)
            print(
                f"Attempt {attempt} for {region['country']}: HTTP {response.status_code}, "
                f"content-type={response.headers.get('content-type')}, "
                f"body-length={len(response.content)}"
            )

            if response.status_code != 200:
                print(f"Non-200 response body (first 300 chars): {response.text[:300]!r}")
                last_error = f"HTTP {response.status_code}"
            else:
                payload = decode_payload(response.text)
                if payload is not None:
                    return payload
                print(f"Body could not be decoded as JSON or compressed JSON (first 300 chars): {response.text[:300]!r}")
                last_error = 'decode_failed'
        except requests.RequestException as e:
            print(f"Request exception on attempt {attempt} for {region['country']}: {e}")
            last_error = e

        if attempt < MAX_RETRIES:
            sleep_for = RETRY_BACKOFF_SECONDS * attempt
            print(f"Retrying in {sleep_for}s...")
            time.sleep(sleep_for)

    print(f"Error fetching data for {region['country']} after {MAX_RETRIES} attempts: {last_error}")
    return None


def sanitize_xml_text(value):
    if value is None:
        return ''
    text = str(value)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def normalize_xmltv_datetime(value):
    if not value:
        return ''
    text = str(value).strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime('%Y%m%d%H%M%S %z')
    except ValueError:
        return text.replace('-', '').replace(':', '').replace('T', ' ').replace('Z', ' +0000').strip()


def generate_files(data, region):
    if not data or 'categories' not in data:
        return False

    epg_url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{region['epg_filename']}"
    m3u_lines = [f'#EXTM3U x-tvg-url="{epg_url}"']
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
    processed_channels = set()

    for category in data.get('categories', []):
        cat_name = str(category.get('categoryName') or 'General')
        for chan in category.get('channels', []):
            chan_id = str(chan.get('channelId') or '').strip()
            if not chan_id or chan_id in processed_channels:
                continue

            chan_name = sanitize_xml_text(chan.get('channelName') or 'Unknown')
            stream_url = str(chan.get('mediaStaticUrl') or '').split('?')[0].strip()
            if not stream_url:
                continue

            programs = chan.get('programs') or []
            logo = ''
            if programs and programs[0].get('imageUrl'):
                logo = programs[0].get('imageUrl')

            m3u_lines.append(
                f'#EXTINF:-1 tvg-id="{chan_id}" tvg-name="{chan_name}" tvg-logo="{logo}" group-title="{sanitize_xml_text(cat_name)}",{chan_name}'
            )
            m3u_lines.append(stream_url)

            xml_lines.append(f'  <channel id="{chan_id}">')
            xml_lines.append(f'    <display-name>{chan_name}</display-name>')
            xml_lines.append('  </channel>')

            for prog in programs:
                start = normalize_xmltv_datetime(prog.get('startDateTime'))
                end = normalize_xmltv_datetime(prog.get('endDateTime'))
                title = sanitize_xml_text(prog.get('programTitle') or 'No Title')
                desc = sanitize_xml_text(prog.get('description') or '')
                if start and end:
                    xml_lines.append(f'  <programme start="{start}" stop="{end}" channel="{chan_id}">')
                    xml_lines.append(f'    <title>{title}</title>')
                    xml_lines.append(f'    <desc>{desc}</desc>')
                    xml_lines.append('  </programme>')

            processed_channels.add(chan_id)

    xml_lines.append('</tv>')

    with open(region['m3u_filename'], 'w', encoding='utf-8') as f:
        f.write('\n'.join(m3u_lines))

    with open(region['epg_filename'], 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))

    return True


if __name__ == '__main__':
    produced_any = False

    for region_name, region in REGIONS.items():
        print(f"Generating playlist for {region_name.upper()} region: {region['country']}")
        fetched = fetch_data(region)
        if fetched is None:
            print(f"Aborting region {region_name.upper()}: no data fetched, leaving existing files untouched.")
            continue

        if generate_files(fetched, region):
            produced_any = True

    if not produced_any:
        print('No LG region data was available, failing the job to avoid stale output.')
        sys.exit(1)
