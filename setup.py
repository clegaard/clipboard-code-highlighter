from setuptools import setup, find_packages


setup(
    name="clipper",
    description="Automatically export code in clipboard as SVG graphics using Pygments-backend",
    url="https://github.com/clegaard/clipboard-code-highlighter",
    version="0.0.1",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=["pygments", "pyperclip", "regex"],
    entry_points={"console_scripts": ["clipper=clipper.clipper_cli:main"]},
)
