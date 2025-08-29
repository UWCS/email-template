# UWCS-branded HTML and Markdown templating

Adapted part of `sec-scripts`, this repo is intended to be an easy-to-find place for templates commonly used in writing emails, without extra baggage when re-using.
- `template.html` contains the base template, with placeholders for `title`, `content` and `sponsors` that should all be replaced with the relevant HTML (or removed)
- `./sponsors` contains tier-separated markdown for sponsors
- `md2html.py` contains a simple script that converts given markdown into HTML:
  - For this script, you need `markdown-it-py==3.0.0`, `mdit-py-plugins==0.4.2` and (if below Python 3.11) `tomli==2.2.1`
  - You can install these via `python -m pip install -r requirements.txt`
  - The script can be run via the command line or via importing and calling `create_html` with keyword arguments, with the following options provided:
    - Command line: `-b`/`--basic`, function argument: `no_template` - Generate a plain HTML equivalent of the markdown file, without using `template.html` or `sponsors.md`. This is `False` if not provided.
    - Command line: `-f`/`--filename`, function argument: `filename` - Target markdown file to generate HTML for. This is `your_content_here.md` if not provided. Example: `-f woah.md`. Assumes current working directory rather than script invocation path (important when submoduling).
    - Command line: `-rt`/`--remove-title`, function argument: `remove_title`  - Ignore any `title` field found in markdown frontmatter - only relevant if you're e.g. trying to convert a markdown file from `stardust`. This is `False` if not provided.
    - Command line: `-rb`/`--remove-bronze-sponsors`, function argument: `remove_bronze_sponsors` - Don't insert HTML for `sponsors/03-bronze.md`. This is False if not provided.
    - Command line: `-rs`/`--remove-sponsors`, function argument: `remove_sponsors` - Don't insert HTML for `sponsors.md`. This is `False` if not provided. This takes precedence over `remove_bronze_sponsors`.
