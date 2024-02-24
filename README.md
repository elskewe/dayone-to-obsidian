# dayone-to-obsidian

Convert a [Day One](https://dayoneapp.com/) JSON export into individual entries for [Obsidian](https://obsidian.md).

Heavily based off of the work from [QuantumGardener](https://github.com/quantumgardener/dayone-to-obsidian) and [edoardob90](https://github.com/edoardob90/dayone-to-obsidian) with a few improvements.

## Added features

Check the `--help` option to get a description of the new features. 

Changes by [edoardob90](https://github.com/edoardob90):

- Process audio, video, and pdf attachments as well
- Toggle on/off YAML frontmatter (if you don't want it or use it)
- Add option `--convert-links` to replace internal DayOne links (e.g., `dayone://view?entryId=<UUID>`) with Obsidian links
- Status tags can be added with the `--status-tags` (or `-s`). Each `tag` passed as argument will be added as `#status/tag`
- Add the option `--merge-entries` to merge entries (with a custom separator) with the same date instead of creating multiple files

Changes by [me](https://github.com/elskewe):

- Adjust for slight changes in the Day One JSON export
- Fix quoting in YAML frontmatter
- Write location as number instead of strings (this enables using the [Map View plugin](obsidian://show-plugin?id=obsidian-map-view) in Obsidian)
- Either a YAML frontmatter or the metadate in the text is written, not both when enabling the YAML frontmatter
- Combine the time and date into a single field
- Fix links across journals (links are now relative instead of just the filename)


## Installation

- Clone the repository
- Run `poetry install`
- Run `poetry run python import.py path/to/folder`

You can also run **without Poetry**: you can simply create a virtual environment and run `pip install -r requirements.txt` since the script requires only a couple of packages not in Python standard library.

## Day One version

This script works with journals exported as JSON from DayOne, version **2024.03** (Android) as of February, 18th 2024.

## Setup

| :warning: WARNING                                  |
| :------------------------------------------------- |
| This script deletes folders if run a second time   |
| You are responsible for ensuring against data loss |
| This script renames files (namely, media files)    |

1. Export your journal from [Day One in JSON format](https://help.dayoneapp.com/en/articles/440668-exporting-entries)
2. Expand that zip file
3. Run the script as shown above
4. Check results in Obsidian by opening the folder as a vault
5. If happy, move each _journal name_, _photos_, and _pdfs_ folders to another vault.

_Suggestion:_ to move the outputted Markdown files, it's convenient to use `rsync`. For example,

```bash
rsync -R -av --inplace --update export_folder/ vault_folder/
```

and `rsync` will re-create the exact folder structure.

## Features

### Config file

If you want to import the same journal periodically, you ideally want to run the `import.py` script with the same options. For this purpose, the script supports reading a YAML configuration file with the `-c/--config` option.

The YAML config file recognizes keywords with the same names as command-line options. Additionally, you can add a `metadata` key which contains any extra metadata field you might want to add to **each entry**.

Command-line options have precedence on the corresponding key-value in the config file, i.e., you can use a command-line option to override whatever value is set in the config file.

The only keys which are **not** discarded when the equivalent command-line option is passed are `ignore_tags` and `status_tags`. In this case, the values passed when invoking the script are **merged** with those found in the config file (if any).

An example of a valid `config.yaml` is:

```yaml
vault_directory: ~/path/to/my/journal/folder/
yaml: true
merge_entries: true
convert_links: false
ignore_tags:
  - First tag to ignore
  - Another tag to ignore
status_tags:
  - Draft
  - From email
metadata:
  up: 'A new metadata field named "up" will be added'
  note: |
    This note field can be a
    multiline text.
    It can also contain

    empty lines, if that's what you want.

  # Additional tags will be added to EVERY entry.
  # Make sure this is what you want.
  tags:
    - Additional tag 1
    - Additional tag 2
```

A few notes about the YAML format:

- YAML doesn't require strings to be quoted. However, you might want to quote them to preserve their content as-is.
- If you leave a key with no value, Python will assign a default `None` to that key.

### Metadata formatting

The metadata formatting choices were dictated by purely personal criteria. In other words, the files are formatted the way I want them in my Obsidian vault.

An example of a metadata block:

```
dates:: <entry date (YYYY-MM-DD)>
time:: <entry time (HH:MM, localized)>
places:: <entry address>
location:: <GPS coordinates (if present)>
weather:: <weather conditions>
tags:: #journal/journalName #prefix/tag1, #prefix/tag2 #status/statusTag1 #place/country/region/town
url:: [DayOne](dayone://view?entryId=<uuid>)
```

That said, the formatting can be adapted to one's purposes very easily. If you are comfortable in editing the source code and have some experience with Python, take a look at the definition of the `Entry` class at the beginning of `utils.py` and adjust the `__str__` method to change the formatting.

## Todo

Features I'm considering:

- [x] Specify the vault destination folder to skip files that are already present
- [x] Add possibility to read in options from a config file (ideally a `config.yaml`)
- [ ] Add the possibility to customize metadata formatting (not sure to which template it should adhere)
- [ ] Implement a copy with `rsync`
- [ ] Auto-unzip of the exported journal
