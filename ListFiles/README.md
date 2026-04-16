# ListFilesSideBySide

This script visually lists files side by side. This requires you to provide 2 paths/ directories and it will list files alphabetically and basically show files if it exists in both directories. Take note that this only lists file in the directory and not in the subdirectory (NO RECURSIVE CHECKING)

## listFilesSideBySide.py
### Prerequisites
1. Install textual package by using the command below<br/>
`pip install -r requirements.txt`<br/>
### Command<br/>
`python listFilesSideBySide.py 「absolute path for directory 1」 「absolute path for directory 2」...「up to 4 directories separated by space」`<br/>

## listFilesByDate.py
### Prerequisites
1. Install textual package by using the command below<br/>
`pip install -r requirements.txt`<br/>
### Command<br/>
`python listFilesByDate.py --dir /path`<br/>
`python listFilesByDate.py --dir /path -n 5 --modified`<br/>
`python listFilesByDate.py --dir /path --modified`<br/>