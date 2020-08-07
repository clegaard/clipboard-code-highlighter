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
    Whitespace,
)
from pygments.lexers import get_lexer_by_name
from pygments.formatters import get_formatter_by_name

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG)

#
# class VSCodeLight(Style):
#     styles = {
#         Comment: "#008000",
#         Keyword: "#0000FF",
#         # Name: "#f00",
#         # Name.Function: "#0f0",
#         # Name.Class: "bold #0f0",
#         String: "#A31515",
#     }


class VSCodeLight(Style):
    """
    Replicate the "Light (Visual Studio)"-theme in pygments
    """

    default_style = ""

    styles = {
        Whitespace: "#bbbbbb",
        Comment: "#008000",
        Comment.Preproc: "#0000FF",
        Comment.Special: "noitalic bold",
        String: "#A31515",
        String.Char: "#800080",
        Number: "#098658",
        Keyword: "#0000FF",
        Operator.Word: "bold",
        Name.Tag: "bold #000080",
        Name.Attribute: "#FF0000",
        Generic.Heading: "#999999",
        Generic.Subheading: "#aaaaaa",
        Generic.Deleted: "bg:#ffdddd #000000",
        Generic.Inserted: "bg:#ddffdd #000000",
        Generic.Error: "#aa0000",
        Generic.Emph: "italic",
        Generic.Strong: "bold",
        Generic.Prompt: "#555555",
        Generic.Output: "#888888",
        Generic.Traceback: "#aa0000",
        Error: "bg:#e3d2d2 #a61717",
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


def main():
    parser = argparse.ArgumentParser(
        prog="clipper",
        description="Automated highlighting and export of code in clipboard using Pygments. For available lexers and formatters refer to output from 'pygmentize -L'",
    )
    parser.add_argument(
        "--lexer", default="c", help="which lexer/language to use for parsing code",
    )
    parser.add_argument(
        "--formatter",
        default="svg",
        choices=["svg"],
        help="formatter to use for exporting code",
    )

    parser.add_argument(
        "--line-numbers",
        dest="line_numbers",
        action="store_true",
        help="add line numbers to generated output",
    )

    parser.add_argument(
        "--crop",
        action="store_true",
        help="attempt to set the height and width of the svg file to fit contents",
    )

    overwrite_clipboard_group = parser.add_mutually_exclusive_group()

    overwrite_clipboard_group.add_argument(
        "--overwrite-clipboard-text",
        dest="overwrite_clipboard_text",
        action="store_true",
        help="copy the textual representation of the result into the clipboard",
    )

    overwrite_clipboard_group.add_argument(
        "--overwrite-clipboard-file",
        dest="overwrite_clipboard_file",
        action="store_true",
        help="copy the results into the clipboard as a reference to the stored file",
    )

    parser.add_argument(
        "--outdir",
        default="clipper_snippets",
        help="directory into which the exported snippets are saved",
    )

    # parse arguments
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)

    # handle clipping

    while True:

        lexer = get_lexer_by_name(args.lexer)
        formatter = get_formatter_by_name(
            args.formatter, style=VSCodeLight, linenos=args.line_numbers
        )

        logger.info("waiting for new paste")
        s = pyperclip.waitForNewPaste()

        assert type(s) is str

        try:
            if s not in {"", None}:
                print(s)
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

                if args.overwrite_clipboard_text:
                    pyperclip.copy(svg)

                if args.overwrite_clipboard_file:
                    raise NotImplementedError("Not implemented")

                logger.info(f"Snippet stores as: {outfile}")
            else:
                logger.warning(
                    "Contents of clipboard appears to be empty, no snippet generated"
                )
        except:
            logger.error(
                "An exception was raised when parsing clipboard, no snippet generated",
                exc_info=True,
            )
