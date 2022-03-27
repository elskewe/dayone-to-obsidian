# dayone-to-obsidian
Convert a [Day One](https://dayoneapp.com/) JSON export into individual entries for [Obsidian](https://obsidian.md). ~~Each entry is created as a separate page.~~

Heavily based off the work from [QuantumGardener](https://github.com/quantumgardener/dayone-to-obsidian) with a few improvements.

## Added features of this repo

Check the `--help` option to get a description of the new features. In summary:

- Process audio attachments as well
- Toggle on/off YAML frontmatter (if you don't want it or use it)
- Add option to replace internal DayOne links (e.g., `dayone://view?entryId=<UUID>`) with Obsidian links
- Add option to convert `#tags` to `[[links]]`
  - There's also the option to keep certain tags as is, adding them to the `Status` field in the metadata section
- Add the option to merge entries (with a custom separator) with the same date instead of creating multiple files

## Installation
- Clone the repository
- Run ``poetry install``
- Run ``poetry run python import.py path/to/folder``

Without Poetry, you can simply create a virtual environment and run `pip install -r requirements.txt` since the script requires only a couple of packages not in Python standard library.

## Optional requirements
* Obsidian [Icons Plugin](https://github.com/visini/obsidian-icons-plugin) to display calendar marker at start of page heading. Enable by passing:
* If you use the [Icons Plugin](https://github.com/visini/obsidian-icons-plugin) to display calendar marker at start of page heading pass ``--icons``
  * ``poetry run python import.py --icons true path/to/folder``

## Day One version
This script works with version the latest version available of DayOne, **7.3** (build 1380) as of March, 27th 2022.

## Setup

**This script deletes folders if run a second time**
**You are responsible for ensuring against data loss**
**This script renames files** (namely, media files)

1. Export your journal from [Day One in JSON format](https://help.dayoneapp.com/en/articles/440668-exporting-entries) 
2. Expand that zip file
3. Run the script as shown above
4. Check results in Obsidian by opening the folder as a vault
5. If happy, move each *journal name*, *photos*, and *pdfs* folders to another vault.

## Features
* Processes all entries, including any blank ones you may have.
* Entries are organised by year/month/day.
* If multiple entries on a day, each additional entry is treated seperately
* Adds metadata for whatever exists at bottom of file
   * minimum date and timezone
   * Location as text, linked to a page
   * Tags and starred flag as tag
   * Weather and user activity
* Every entry has the date inserted in the text for easier reading (with a calendar icon to help you quickly distinguish from other entries in your vault)
* If location is specified, it is given under the date, linked to Google Search
* Tags can be prefixed (default is `journal/`) to show as subtags in Obsidian separate from other note tags. Use ``--tags-prefix`` option to customize the prefix
* Run with `--help` for options
