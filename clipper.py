import logging
import argparse
from datetime import datetime
from pathlib import Path

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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="clipper")
    parser.add_argument(
        "--lexer", default="c", help="which lexer to use for parsing code"
    )
    parser.add_argument(
        "--formatter", default="svg", help="formatter to use for exporting code"
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

            with open(outfile, "w") as f:
                out = pygments.highlight(code=s, lexer=lexer, formatter=formatter)
                f.write(out)
                if args.overwrite_clipboard:
                    pyperclip.copy(out)

            logger.info(f"Snippet stores as: {outfile}")

