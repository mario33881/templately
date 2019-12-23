# TEMPLATELY

Templately enables you to inject files content inside a main template file.

[Read more about templately's code here](https://mario33881.github.io/templately/)

## Readme sections
* [Why](#why)
* [Usage](#usage)
* [Code documentation](#code-documentation-)
* [Test the script](#test-the-script)
* [Build the docs](#build-the-docs)
* [Requirements](#requirements-)
* [Changelog](#changelog-)
* [Author](#author-)

## Why

This script was made to be used for Dockerfile files:
the development and deployment Dockerfiles for apache with HTTPS enabled
that I had to use lately were slightly different, specifically they were different for the certificate creation,
everything else was the same.

Having to maintain two similar Dockerfiles could have led to human error,
this is why templately was created.

[Go to the top](#readme-sections)

## Usage
```
Usage:
 templately.py [--ot=<opening_tag>] [--po=<pattern_opening>] [--ct=<closing_tag>]
                     <template> <output> <placeholder=file>...
 templately.py (-h | --help)
 templately.py --version

Options:
 -h --help     Show this screen.
 --version     Show version.


Details:
- <template> is the template file
- <placeholder=file> : * "placeholder" is the string to search inside the template
                       * "file" is a file path of which contents gets injected inside the template
                       > "=" is the char that divides placeholder and the file path
```

Example of usage with test files:

The test files are:
    
1. ```template.txt``` content:

        this is
        {{ ty.placeholder1 }} a {{ ty.placeholder2 }}
        test {{ ty.placeholder3 }}

2. ```file1.txt``` content:

        ----
        this
        is placeholder1
        content
        ----

3. ```file2.txt``` content:

        ----
        this
        is placeholder2
        content
        ----

4. ```file3.txt``` content:

        ----
        this
        is placeholder3
        content
        ----

Execute the script with the template path, the output path and the "files to inject" paths

    python templately.py ../test/template.txt output.txt placeholder1=../test/file1.txt placeholder2=../test/file2.txt placeholder3=../test/file3.txt

> ```placeholder1```'s file content will substitute ```{{ ty.placeholder1 }}```,
> the file's path is ```../test/file1.txt```

> ```placeholder2```'s file content will substitute ```{{ ty.placeholder2 }}```,
> the file's path is ```../test/file2.txt```

> ```placeholder3```'s file content will substitute ```{{ ty.placeholder3 }}```,
> the file's path is ```../test/file3.txt```

This is the content of the output file:

    this is
    ----
    this
    is placeholder1
    content
    ---- a ----
    this
    is placeholder2
    content
    ----
    test ----
    this
    is placeholder3
    content
    ----

[Go to the top](#readme-sections)

## Code documentation ![](https://i.imgur.com/wMdaLI0.png)
Basically this script reads the template file,
checks that the input has the same placeholders of the template file
and lastly writes to the output file the template content and the "files to inject" content.

Most of the code is just for input verication.

[Read more about templately's code here](https://mario33881.github.io/templately/)

[Go to the top](#readme-sections)

## Test the script
To test the script use the test.py script inside the test folder

    python test.py

[Go to the top](#readme-sections)

## Build the docs
To build the docs use the makedocs.bat file if you are on windows,
if you are not on windows use:

    sphinx-build -b html docssrc docs
> The .bat file also writes the coverage of the docs inside the docs/python.txt file,
for other OSes use the same command above with "coverage" instead of "html"

[Go to the top](#readme-sections)

## Requirements ![](https://i.imgur.com/H3oBumq.png)
* python 3

[Go to the top](#readme-sections)

## Changelog ![](https://i.imgur.com/SDKHpak.png)

**01_01 2019-12-23:** <br>
First commit

[Go to the top](#readme-sections)

# Author ![](https://i.imgur.com/ej4EVF6.png)
Zenaro Stefano ( [Github](https://github.com/mario33881) )