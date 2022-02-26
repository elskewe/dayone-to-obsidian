from __future__ import annotations

from collections import namedtuple
from json.decoder import JSONDecodeError

import dateutil.parser

import click
import json
import pytz
import re
import os
import sys
import shutil
import typing

if typing.TYPE_CHECKING:
    from pathlib import Path


# Used to produce somewhat structured metadata entries
MetadataEntry = namedtuple("MetadataEntry", ["name", "description"])


def retrieve_metadata(entry, localDate, location, tagPrefix):
    metadata = []
    metadata.append(MetadataEntry(name="dayone_uuid", description=entry["uuid"]))

    # Add raw create datetime adjusted for timezone and identify timezone
    metadata.append(
        MetadataEntry(
            name="Creation Date",
            description=f"{localDate.isoformat(), entry['timeZone']}",
        )
    )

    if location:
        metadata.append(MetadataEntry(name="location name", description=location))

    # Add GPS, not all entries have this
    if "location" in entry and all(
        ["latitude" in entry["location"], "longitude" in entry["location"]]
    ):
        lat = entry["location"]["latitude"]
        lon = entry["location"]["longitude"]

        metadata.append(
            MetadataEntry(
                name="location",
                description=f"[{lat},{lon}]",
            )
        )
        metadata.append(
            MetadataEntry(
                name="GPS",
                description=f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
            )
        )

    # Add weather information if present
    if "weather" in entry and all(
        [
            i in entry["weather"]
            for i in ["conditionsDescription", "temperatureCelsius", "windSpeedKPH"]
        ]
    ):
        w = entry["weather"]
        metadata.append(
            MetadataEntry(
                name="Weather",
                description=f"{w['conditionsDescription']}, {w['temperatureCelsius']}°C, {w['windSpeedKPH']} kph wind",
            )
        )

    # Add user activity if present
    if "userActivity" in entry and "stepCount" in entry["userActivity"]:
        metadata.append(
            MetadataEntry(name="Steps", description=entry["userActivity"]["stepCount"])
        )

    tags = []
    if "tags" in entry:
        tags = []
        for t in entry["tags"]:
            tags.append("%s%s" % (tagPrefix, t.replace(" ", "-").replace("---", "-")))
        if entry["starred"]:
            tags.append("%sstarred" % (tagPrefix))
    if len(tags) > 0:
        metadata.append(MetadataEntry(name="tags", description=",".join(tags)))

    return metadata


def process_journal(journal: Path, icons: bool, tagPrefix: str, verbose: int):
    """Converts all entries in the JSON files to markdown files"""
    journal_name = (
        journal.stem.lower()
    )  # name of folder where journal entries will end up in your Obsidian vault
    base_folder = journal.resolve().parent 
    journal_folder = base_folder / journal_name

    # Clean out existing journal folder, otherwise each run creates new files
    if journal_folder.exists():
        if verbose > 0:
            click.echo(f"Deleting existing folder: {journal_folder}")
        shutil.rmtree(journal_folder)

    if verbose > 0:
        click.echo(f"Creating {journal_folder}")
    journal_folder.mkdir()

    if icons:
        if verbose > 0:
            click.echo("Icons are on")
        date_icon = "`fas:CalendarAlt` "
    else:
        if verbose > 0:
            click.echo("Icons are off")
        date_icon = ""  # make 2nd level heading

    click.echo(f"Begin processing entries for '{journal.name}'")

    with open(journal, encoding="utf-8") as json_file:
        data = json.load(json_file)
        for count, entry in enumerate(data["entries"], start=1):
            new_entry = []

            createDate = dateutil.parser.isoparse(entry["creationDate"])
            localDate = createDate.astimezone(
                pytz.timezone(entry["timeZone"])
            )  # It's natural to use our local date/time as reference point, not UTC

            # Add location
            location = ""
            for locale in [
                "placeName",
                "localityName",
                "administrativeArea",
                "country",
            ]:
                try:
                    location = "%s, %s" % (location, entry["location"][locale])
                except KeyError:
                    pass
            location = location[2:]

            # add some metadata as front matter
            metadata = retrieve_metadata(entry, localDate, location, tagPrefix)
            new_entry.append("---\n")
            for name, description in metadata:
                if name in ["location", "location name", "tags"]:
                    new_entry.append(f"{name}: {description}\n")
            new_entry.append("---\n")

            # Add date as page header, removing time if it's 12 midday as time obviously not read
            if sys.platform == "win32":
                new_entry.append(
                    "## %s%s\n"
                    % (
                        date_icon,
                        localDate.strftime("%A, %#d %B %Y at %#I:%M %p").replace(
                            " at 12:00 PM", ""
                        ),
                    )
                )
            else:
                new_entry.append(
                    "## %s%s\n"
                    % (
                        date_icon,
                        localDate.strftime("%A, %-d %B %Y at %-I:%M %p").replace(
                            " at 12:00 PM", ""
                        ),
                    )
                )  # untested

            # Add body text if it exists (can have the odd blank entry), after some tidying up
            try:
                new_text = entry["text"].replace("\\", "")
                new_text = new_text.replace("\u2028", "\n")
                new_text = new_text.replace("\u1C6A", "\n\n")

                if "photos" in entry:
                    # Correct photo links. First we need to rename them. The filename is the md5 code, not the identifier
                    # subsequently used in the text. Then we can amend the text to match. Will only to rename on first run
                    # through as then, they are all renamed.
                    # Assuming all jpeg extensions.
                    for p in entry["photos"]:
                        image_type = p["type"]
                        original_photo_file = (
                            base_folder
                            / "photos"
                            / f"{p['md5']}.{image_type}"
                        )
                        renamed_photo_file = (
                            base_folder
                            / "photos"
                            / f"{p['identifier']}.{image_type}"
                        )
                        if original_photo_file.exists():
                            if verbose > 1:
                                click.echo(
                                    f"Renaming {original_photo_file} to {renamed_photo_file}"
                                )
                            original_photo_file.rename(renamed_photo_file)

                        # Now to replace the text to point to the file in obsidian
                        new_text = re.sub(
                            r"(\!\[\]\(dayone-moment:\/\/)([A-F0-9]+)(\))",
                            (r"![[\2.%s]]" % image_type),
                            new_text,
                        )

                if "pdfAttachments" in entry:
                    # Correct photo pdf links. Similar to what is done on photos
                    for p in entry["pdfAttachments"]:
                        original_pdf_file = (
                            base_folder / "pdfs" / f"{p['md5']}.pdf"
                        )
                        renamed_pdf_file = (
                            base_folder
                            / "pdfs"
                            / f"{p['identifier']}.pdf"
                        )
                        if original_pdf_file.exists():
                            if verbose > 1:
                                click.echo(
                                    f"Renaming {original_pdf_file} to {renamed_pdf_file}"
                                )
                            original_pdf_file.rename(renamed_pdf_file)

                        # Now to replace the text to point to the file in obsidian
                        new_text = re.sub(
                            r"(\!\[\]\(dayone-moment:\/pdfAttachment\/)([A-F0-9]+)(\))",
                            r"![[\2.pdf]]",
                            new_text,
                        )

                new_entry.append(new_text)
            except KeyError:
                pass

            ## Start Metadata section

            # newEntry.append( '%%\n' ) #uncomment to hide metadata

            metadata = retrieve_metadata(entry, localDate, location, tagPrefix)
            new_entry.append("\n\n---\n")
            new_entry.append("**Metadata**\n")
            for name, description in metadata:
                new_entry.append(f"- {name}: {description}\n")

            # Save entries organised by year, year-month, year-month-day.md
            year_dir = journal_folder / str(createDate.year)
            month_dir = year_dir / createDate.strftime("%Y-%m")

            if not year_dir.exists():
                year_dir.mkdir()

            if not os.path.isdir(month_dir):
                month_dir.mkdir()

            # Attempt to get the header to make a better note filename
            # first_line = ""
            # if "richText" in entry:
            #     try:
            #         rich_text = json.loads(entry["richText"])
            #         first_line = " " + rich_text["contents"][0]["text"].strip()
            #     except (JSONDecodeError, KeyError):
            #         pass

            # Target filename to save to. Will be modified if already exists
            file_date_format = localDate.strftime("%Y-%m-%d")
            target_file = month_dir / f"{file_date_format}.md"

            # Here is where we handle multiple entries on the same day. Each goes to it's own file
            if target_file.exists():
                # File exists, need to find the next in sequence and append alpha character marker
                index = 97  # ASCII a
                target_file = month_dir / f"{file_date_format}{chr(index)}.md"
                while target_file.exists():
                    index += 1
                    target_file = month_dir / f"{file_date_format}{chr(index)}.md"

            with open(target_file, "w", encoding="utf-8") as f:
                for line in new_entry:
                    f.write(line)

        click.echo(f"Complete: {count} entries processed.")
