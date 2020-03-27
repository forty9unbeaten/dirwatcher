# DirWatcher

A CLI Python long-running program that monitors a directory in your file structure, reads the data from each file with a specified extension in the directory, and logs when a specified string of text is found in one of the files. The directory is monitored until the user intervenes. The program dynamically reports/logs its findings.

## Getting Started

After forking and cloning the repository, a requirements.txt document can be used to create a Python virtual environment with the appropriate packages.

### Python Packages

```
entrypoints==0.3
flake8==3.7.9
mccabe==0.6.1
pycodestyle==2.5.0
pyflakes==2.1.1
```

### Command-Line Arguments

#### CLI Usage

```
python3 dirwatcher.py [-h] [-i,--interval] [-l,--loglevel] dir ext text
```

#### Positional/Required Arguments

```
dir ~ The directory the program needs to monitor
ext ~ The extension of the files the program will read
text ~ The string of text the program should look for in file data
```

#### Optional Arguments

```
-h ~ Display the help menu
-i, --interval ~ The frequency that the program looks at file data (defaults to every 1 second)
-l, --loglevel ~ Determines the verbosity of program logging (defaults to INFO)
```

#### CLI Example

```
python3 dirwatcher.py -i 3 -l 1 . .txt "Hello World"
```

The above example will:

- Search the current directory
- Dynamically read lines in .txt files
- Look for 'Hello World' in .txt file lines
- Look for appended lines and new files every 3 seconds
- Log on a DEBUG level, providing the most possible information

## Author

- **Rob Spears** - [Forty9Unbeaten](https://github.com/Forty9Unbeaten)
