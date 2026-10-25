1| Fork this for more languages: https://github.com/BuddyChewChew/lg-playlist-generator/issues/1#issuecomment-4041402810
2| 
3| # ⭐ LG WEB Channel M3U Playlist Generator
4| 
5| [![Update LG Playlist](https://github.com/BuddyChewChew/lg-playlist-generator/actions/workflows/update_lg.yml/badge.svg)](https://github.com/BuddyChewChew/lg-playlist-generator/actions/workflows/update_lg.yml)
6| 
7| This repository automatically generates M3U playlist files for LG Channels using a Python script and GitHub Actions. The playlists include embedded EPG (Electronic Program Guide) information via the generated XML files.
8| 
9| ## 🟢 Service Status & Playlist URLs
10| 
11| | Service | Status | Region Support | Playlist URL (M3U) | EPG / Guide Source |
12| | :--- | :--- | :--- | :--- | :--- |
13| | **LG Channels** | ✅ Online | US | `lg_channels_us.m3u` | `lg_channels_us.xml` (Self-Generated) |
14| | **LG Channels** | ✅ Online | GB | `lg_channels_gb.m3u` | `lg_channels_gb.xml` (Self-Generated) |
15| 
16| ---
17| 
18| ## ▶️ How It Works
19| 
20| 1. **Data Fetching:** A Python script (`lg_gen.py`) fetches the latest channel and program data directly from the LG Channels API.
21| 2. **M3U Generation:** The script parses the live data, cleans stream URLs, and categorizes channels by genre.
22| 3. **GitHub Action:** A scheduled workflow runs every 6 hours to ensure links and guide data are up to date.
23| 4. **The TiviMate Fix:** The workflow dynamically injects the full GitHub Raw URL for the EPG into the M3U header. This ensures that players like TiviMate or OTT Navigator find the guide automatically.
24| 
25| ## ▶️ Services Included
26| 
27| ### 🔹 LG Channels (US)
28| **File:** `lg_channels_us.m3u`
| * **Features:** Full linear lineup, channel logos, and 24-hour program descriptions.
|
| ### 🔹 LG Channels (GB)
| **File:** `lg_channels_gb.m3u`
| * **Features:** Full linear lineup, channel logos, and 24-hour program descriptions.
|
| ---
|
| ## ▶️ How to Use
|
| The generated M3U files are located in the repository root.
|
| **Direct URL Format (US):**
| `https://raw.githubusercontent.com/justme-uk/lgtv/main/lg_channels_us.m3u`
|
| **Direct URL Format (GB):**
| `https://raw.githubusercontent.com/justme-uk/lgtv/main/lg_channels_gb.m3u`
|
| ## ▶️ Update Schedule
|
| Playlists are automatically updated every 6 hours via GitHub Actions. Your IPTV player should periodically refresh the URL to get the latest channel updates.
|
| ## ▶️ Disclaimer
|
| * This repository aggregates publicly available channel information.
| * Availability and stability of streams depend entirely on the original service providers.
| * Ensure your use of these streams complies with the terms of service of the respective platforms.
