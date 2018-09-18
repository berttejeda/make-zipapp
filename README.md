## Overview

A python script that creates a self-contained zip application from a specified python script.

## Usage Examples

Suppose you want to bundle in your python script dependencies.

Assume you store these modules under a folder named 'lib'

You can easily create your zip app as follows:

```
mkdir lib
pip install -t lib -r requirements.txt
make-zipapp -f myscript.py
```

By default, the program will bundle in anything located in the local 'lib' folder

You can also specify multiple dependencies, folders or files, as follows:

```
make-zipapp -f myscript.py -d lib conf config.ini
```

The script will create a zip application named after the specified python file, with the file extension stripped.

So the above command will produce a binary file named **myscript**

If you invoked `make-zipapp`  from a posix-compliant system, the resulting zip application is made executable, and can be called by its path, e.g.

`./myscript`

I've accomplished the same from a Windows machine using [cmder](http://cmder.net/), which includes **git-bash**.

You can also call the zipapp via the `python` executable, as with:

`python ./myscript`
