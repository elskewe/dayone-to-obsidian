import click

from utils import process_journal
from pathlib import Path


@click.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option('-v', '--verbose', count=True)
@click.option("--icons", help="Use the obsidian icons plugin", default=False)
@click.option(
    "--tags-prefix",
    help="Prefix to add as part of the tag name for sub-tags",
    default="#journal/",
)
def convert(verbose, icons, tags_prefix, folder):
    """Converts DayOne entries into markdown files suitable to use as an Obsidian vault.
    Each journal will end up in a sub-folder named after the file (e.g.: Admin.json -> admin/). All JSON files
    in the FOLDER will be processed, remove those you don't want processed. The FOLDER will also be the destination
    for converted markdown files. After conversion you can open this folder as a vault in Obsidian. This is done
    to prevent accidental modification of an existing vault.

    FOLDER is the folder where your DayOne exports reside and where the converted markdown files will be written.
    """
    for filename in Path(folder).glob("*.json"):
        process_journal(filename, bool(icons), tags_prefix, verbose)


if __name__ == "__main__":
    convert()
