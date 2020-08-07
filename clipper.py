import logging
import argparse
from datetime import datetime
from pathlib import Path
import regex as re


import pyperclip
import pygments
from pygments.style import Style
from pygments.token import (
    Keyword,
    Name,
    Comment,
    String,
    Error,
    Number,
    Operator,
    Generic,
)
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name
from pygments.styles import get_style_by_name

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

# Replicate the "Light (VSCode)"-theme in pygments
class VSCodeLight(Style):
    styles = {
        Comment: "#008000",
        Keyword: "#0000FF",
        # Name: "#f00",
        # Name.Function: "#0f0",
        # Name.Class: "bold #0f0",
        String: "#A31515",
    }


def infer_height_and_width(text: str, svg: str):

    # count height by finding text element starting at largets y value. e.g. y="2000" in svg contents
    max_height = max(
        [int(y_str) for y_str in re.findall(pattern=r'<text.*y="([1-9]+)"', string=svg)]
    )

    # count maximum line width by looking at length substrings split by newline or carriage return
    # assumption is that for a given fontsize the line width is directly proportional to the width of the rendered svg
    fontsize = int(re.search(pattern=r'font-size="([0-9]+)px"', string=svg).group(1))
    fontsize_to_width_ratio = 0.65  # tweaking parameter
    assert fontsize > 0
    max_width = int(
        max([len(t) for t in text.splitlines()]) * fontsize * fontsize_to_width_ratio
    )

    return (max_height, max_width)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="clipper")
    parser.add_argument(
        "--lexer", default="c", help="which lexer to use for parsing code"
    )
    parser.add_argument(
        "--formatter", default="svg", help="formatter to use for exporting code"
    )

    parser.add_argument(
        "--crop",
        action="store_true",
        help="try to crop the svg file to fit the highlighted code",
    )

    parser.add_argument(
        "--overwrite-clipboard",
        dest="overwrite_clipboard",
        action="store_true",
        help="copy the results into the clipboard",
    )

    parser.add_argument(
        "--outdir",
        default="clipper_snippets",
        help="directory into which the exported snippets are saved",
    )

    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    while True:

        lexer = get_lexer_by_name(args.lexer)
        formatter = get_formatter_by_name(args.formatter, line_numbers=True,)

        logger.info("waiting for new paste")
        s = pyperclip.waitForNewPaste()

        assert type(s) is str

        if s is not None:
            logger.info(f"The following string was copied to the clipboard:\n{s}")

            ts = datetime.timestamp(datetime.now())
            outfile = outdir / f"{ts}.svg"

            svg = pygments.highlight(code=s, lexer=lexer, formatter=formatter)

            if args.crop:
                height, width = infer_height_and_width(text=s, svg=svg)
                logger.info(f"cropping svg to height:{height} width:{width}")
                from regex import sub

                svg = sub(
                    pattern="<svg",
                    repl=f'<svg height="{height}" width="{width}" ',
                    string=svg,
                )

            with open(outfile, "w") as f:

                f.write(svg)

            if args.overwrite_clipboard:
                pyperclip.copy(svg)

            logger.info(f"Snippet stores as: {outfile}")

