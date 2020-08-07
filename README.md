# clipboard-code-highlighter

Syntax highlighting of clipboard code snippet using [Pygments](https://pygments.org/)

**Work in progress**

# Requirements

- Python 3

# Installing

1. clone the code
2. cd into root of repo
3. install using pip

```bash
pip install .
```

# Usage

The command line utility, _clipper_ can be invoked directly from the shell

```bash
clipper
```

The program waits for content to be copied into the clipboard. When code is copied into the clipboard it is parsed, highligted and saved into the specified output folder, per default _clipper_snippets_.

From there the exported file may be dragged into a PowerPoint presentation or similar.

For options refer to the output of the help-command:

```
clipper --help
usage: clipper [-h] [--lexer LEXER] [--formatter {svg}] [--crop] [--overwrite-clipboard-text | --overwrite-clipboard-file] [--outdir OUTDIR]

Automated highlighting and export of code in clipboard using Pygments. For available lexers and formatters refer to output from 'pygmentize -L'

optional arguments:
  -h, --help            show this help message and exit
  --lexer LEXER         which lexer/language to use for parsing code
  --formatter {svg}     formatter to use for exporting code
  --crop                attempt to set the height and width of the svg file to fit contents
  --overwrite-clipboard-text
                        copy the textual representation of the result into the clipboard
  --overwrite-clipboard-file
                        copy the results into the clipboard as a reference to the stored file
  --outdir OUTDIR       directory into which the exported snippets are saved
```
