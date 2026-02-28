from setuptools import setup, find_packages

import os

def read_requirements():
    """Read requirements.txt and return a list of dependencies."""
    if not os.path.exists("requirements.txt"):
        return []
    
    try:
        # Use 'utf-16' to let Python handle the BOM (Byte Order Mark) automatically
        with open("requirements.txt", "r", encoding="utf-16") as f:
            content = f.read()
            # Remove potential BOM character manually if it persists as '\ufeff'
            if content.startswith('\ufeff'):
                content = content[1:]
            lines = content.splitlines()
    except (UnicodeDecodeError, LookupError):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

    requirements = []
    for line in lines:
        # Strip whitespace and common invisible characters
        line = line.strip().replace('\ufeff', '')
        # Skip empty lines, comments, and lines that look like a Python version or title
        if (line and 
            not line.startswith('#') and 
            not line.startswith('Python') and 
            '==' in line or '>=' in line or '<=' in line or '~=' in line):
            requirements.append(line)
    return requirements

setup(
    name="magic-game",
    version="1.0.0",
    author="HAMIC",
    description="A 2D magic fighting game with AI gesture recognition",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    py_modules=["main"],
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "magic-game=main:main",
        ],
    },
    include_package_data=True,
    python_requires=">=3.10",
)
