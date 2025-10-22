"""
Adapted from sec-scripts repository
"""

import os
import re
import sys
import argparse
import pathlib

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # if Python <3.11, need to install via pip install tomli

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin

in_dir = pathlib.Path(__file__).resolve().parent

def filter_front_matter(md_text: str, find_title: bool = False) -> tuple[str, str]:
    """
    Filter out frontmatter e.g. used by Zola in stardust, and extract "title" from said frontmatter if requested

    Example:
    +++
    ...
    +++

    Args:
        md_text (str): Text of the markdown to filter
        find_title (bool, optional): Grab the title from the frontmatter. Defaults to False.

    Returns:
        tuple[str, str]: A tuple containing a string of the filtered markdown content, and a string containing either the found title, or empty if not found/not requested
    """

    fm_match = re.match(r"^\s*\+\+\+\n(.*?)\n\+\+\+\s*\n?", md_text, re.DOTALL)
    if not fm_match:
        return md_text, ""  # return original if no frontmatter
    
    fm_text = fm_match.group(1)
    md_body = md_text[fm_match.end():]
    return md_body, tomllib.loads(fm_text).get("title", "") if find_title else ""

def nl_to_br(match: re.Match) -> str:
    """
    Not currently used.

    Add breaks to newlines in paragraphs so that they render correctly.

    Args:
        match (re.Match): Matched pattern to perform replacement on

    Returns:
        str: Updated content
    """

    content = match.group(1)
    return "<p>" + content.replace("\n", "<br>\n") + "</p>"  # newlines in paragraphs should have breaks added

def open_and_render(filenames: str | tuple[str], rt: bool = False) -> tuple[str, str]:
    """
    With the given filename, render markdown into string with various mdit options to ensure correct formatting.

    Args:
        filenames (str | tuple[str]): Input filenames
        rt (bool, optional): Remove frontmatter title. Defaults to False.

    Returns:
        tuple[str, str]: string containing rendered html, and either string of title, or empty if not found/not requested 
    """

    if type(filenames) is str:
        filenames = [filenames]
    
    md_text = ""
    for filename in filenames:
        with open(filename, encoding="utf8") as f:
            curr_md, title = filter_front_matter(f.read(), find_title=not rt)
            md_text += "\n" * (2 - len(md_text) + len(md_text.rstrip("\n"))) + curr_md

    md = (
        MarkdownIt("commonmark", {"linkify": True, "typographer": True, "breaks": True})    
        .enable("table")
        .enable("strikethrough")
        .enable("autolink")
        .use(tasklists_plugin)
    )

    html = md.render(md_text)
    return html, title

def create_html(filename: str = "your_content_here.md", remove_title: bool = False, remove_sponsors: bool = False, remove_bronze: bool = False, no_template: bool = False) -> None:
    """
    With a given input markdown file, create a html file with the rendered html and options applied

    For example: your_content_here.md will have its html output to your_content_here.html

    Args:
        filename (str, optional): Maps to -f/--filename - markdown target to convert to HTML. Assumes relative to current working directory not the script path
        remove_title (bool, optional): Maps to -rt/--remove-title - will not insert any title found in frontmatter if True. Defaults to False.
        remove_sponsors (bool, optional): Maps to -rs/--remove-sponsors - will not insert any sponsors from sponsors/ if True. Defaults to False.
        remove_bronze (bool, optional): Maps to -rb/--remove-bronze-sponsors - will not insert any sponsors from sponsors/03-bronze.md if True. Defaults to False. remove_sponsors has precedence.
        no_template (bool, optional): Maps to -b/--basic - won't use the template at all and creates plain HTML if True. Defaults to False.
    """

    output = f"{filename.strip('.md')}.html"

    if no_template:
        output_html, _ = open_and_render(filename, True)

    else:
        body_html, title = open_and_render(filename, rt=remove_title)
        
        spon_html, _ = open_and_render(
                [str(in_dir / "sponsors/01-gold.md"), str(in_dir / "sponsors/02-silver.md")]
                + ([str(in_dir / "sponsors/03-bronze.md")] if not remove_bronze else []), False) if not remove_sponsors \
                else ("", "")

        with open(str(in_dir / "template.html"), encoding="utf8") as tpf:
            template = tpf.read()
            output_html = (
                template
                .replace("{{ title }}", title)
                .replace("{{ content }}", body_html)
                .replace("{{ sponsors }}", spon_html)
            )

    with open(output, "w", encoding="utf8") as htmlf:
        htmlf.write(output_html)
        print(f"HTML generated to {output}!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Insert markdown into html template, with optional title and sponsors removal.")
    parser.add_argument("-b", "--basic", action="store_true", help="Convert into normal HTML without the template")
    parser.add_argument("-f", "--filename", type=str, help="Target file to process")
    parser.add_argument("-rt", "--remove-title", action="store_true", help="Don't use frontmatter title from file")
    parser.add_argument("-rb", "--remove-bronze-sponsors", action="store_true", help="Remove Bronze sponsors (e.g. for newsletters)")
    parser.add_argument("-rs", "--remove-sponsors", action="store_true", help="Remove sponsors from file")

    args = parser.parse_args()

    if args.filename is None:
        args.filename = "your_content_here.md"
    
    create_html(os.path.realpath(args.filename), args.remove_title, args.remove_sponsors, args.remove_bronze_sponsors, args.basic)
