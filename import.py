import click
from utils import process_journal
from pathlib import Path

@click.command()
@click.argument("folder", type=click.Path(exists=True, file_okay=False))
@click.option('-v', '--verbose', count=True)
@click.option('--icons/--no-icons', help="Use Obsidian icons plugin", default=False)
@click.option('--yaml/--no-yaml', help="Add a YAML frontmatter", default=True)
@click.option(
    '--convert-links',
    help="Replace DayOne internal links with Obsidian [[links]]",
    default=False,
    is_flag=True
)
@click.option(
    "--tags-prefix",
    help="Prefix to add as part of the tag name for sub-tags",
    default="#journal/",
)
@click.option(
    '--tags-as-links',
    help="Each #tag will be treated as [[links]]. Location name's components will be links as well",
    default=False,
    is_flag=True,
)
@click.option(
    '--status-tag', '-S',
    help="A list of tags that should be added to metadata as 'Status' a not transformed to a [[link]]. Makes sense only if --tags-as-links is passed",
    multiple=True,
    default=list(),
)
@click.option(
    '--merge-entries',
    help="Combine entries with the same date in a single file",
    is_flag=True,
    default=False,
)
def convert(verbose, icons, tags_prefix, folder, convert_links, tags_as_links, yaml, status_tag, merge_entries):
    """Converts DayOne entries into markdown files suitable to use as an Obsidian vault.
    Each journal will end up in a sub-folder named after the file (e.g.: Admin.json -> admin/). All JSON files
    in the FOLDER will be processed, remove those you don't want processed. The FOLDER will also be the destination
    for converted markdown files. After conversion you can open this folder as a vault in Obsidian. This is done
    to prevent accidental modification of an existing vault.

    FOLDER is the folder where your DayOne exports reside and where the converted markdown files will be written.
    """
    # If converting tags to links, remove the tag prefix
    tags_prefix = tags_prefix if not tags_as_links else ''
    
    # Process each JSON journal file in the input folder
    for filename in Path(folder).glob("*.json"):
        process_journal(filename, icons, tags_prefix, verbose, convert_links, tags_as_links, yaml, status_tag, merge_entries)

if __name__ == "__main__":
    convert()
