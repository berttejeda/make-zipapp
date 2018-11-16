#!/usr/bin/env python
# This is a standalone git server implementation in python

import argparse
from argparse import RawTextHelpFormatter
import hashlib
import logging
import os
import re
import shutil
import sys
import zipfile

if sys.version_info[0] == 2:
    print('Not supported on Python 2.x')
    sys.exit(1)

# Private variables
__author__ = 'etejeda@seic.com'
__version__ = '18.07.1332'

# Globals
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root + '/lib')

def get_md5_digest(file_path, block_size=128):
    md5 = hashlib.md5()
    # f = open(file_path).read()
    # return hashlib.md5(f).hexdigest()
    with open(file_path, "rb") as f:
        data = f.read(block_size)
        while len(data) > 0:
            md5.update(data)
            data = f.read(block_size)
    return md5.hexdigest()

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def make_zip(zipapp_file, dependencies):
    """
    Creates a zip-application of itself
    Result is a single executable file
    """
    working_directory = os.getcwd()
    zipapp_name = os.path.basename(zipapp_file).split(".")[0]
    zip_main_file_name = '__main__.py'
    zip_main_file_path = '{d}/{f}'.format(d=working_directory, f=zip_main_file_name)
    # Remove old zip application file
    if os.path.exists(zipapp_name):
        try:
            print("Removing old zip application %s" % zipapp_name)
            os.remove(zipapp_name)
        except OSError:
            print("Could not remove existing zip file {0}".format(zipapp_name))
            pass
    # Create __main__.py script from calling script
    print("Creating {m} from copy of {a}".format(m=zip_main_file_path, a=zipapp_file))
    shutil.copy(zipapp_file, zip_main_file_path)
    # Create zip archive
    print("Creating zip archive %s" % zipapp_name)
    zipf = zipfile.ZipFile(zipapp_name, 'w', zipfile.ZIP_DEFLATED)
    zipf.write(zip_main_file_name)
    for dependency_obj in dependencies:
        if os.path.isfile(dependency_obj):
            zipf.write(dependency_obj)
        elif os.path.isdir(dependency_obj):
            for folder,subfolder,file in os.walk(os.path.join(working_directory, dependency_obj)):
                zip_arcname_mod_len = len(dependency_obj) + 1
                for each in subfolder+file:
                    source = os.path.join(folder,each)
                    # Remove the absolute path to compose arcname
                    # Also handles the remaining leading path separator with lstrip
                    arcname = source[len(working_directory) + zip_arcname_mod_len:].lstrip(os.sep)
                    # Write the file under a different name in the archive
                    #
                    # TODO Employ an exclusion list
                    #
                    zipf.write(source, arcname=arcname)
        else:
            print("Couldn't determine whether %s is a file or directory. Skipping")
            continue
    zipf.close()
    # Write header for zip-application
    print("Writing header for zip application")
    try:
        zip_file_content = open(zipapp_name).read()
        zip_file_exe_header = '#!/usr/bin/env python\n'
    except UnicodeDecodeError:
        zip_file_content = open(zipapp_name, 'rb').read()
        zip_file_exe_header = bytes( '#!/usr/bin/env python\n', 'Utf-8')
    zip_file_content_with_headers = zip_file_exe_header + zip_file_content
    try:
        with open(zipapp_name, 'w') as z:
            z.write(zip_file_content_with_headers)
    except TypeError:
        with open(zipapp_name, 'wb') as z:
            z.write(zip_file_content_with_headers)        
    # Cleanup
    try:
        print("Cleaning up")
        os.remove(zip_main_file_path)
    except OSError:
        print("Could not remove %s" % self.zip_main_file_pat)
        pass
    # Make zip-application executable
    if sys.platform != "win32":
        make_executable(zipapp_name)
    md5_hex_digest = get_md5_digest(zipapp_name)
    print("md5 hash for this executable is:%s" % md5_hex_digest)

# Declare the main() function
def main(args, loglevel):
    logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=loglevel)
    logging.debug("You specified the following file: {f}".format(f=args.file))
    print('Making a zipapp using {f}'.format(f=args.file))
    make_zip(args.file, args.dependencies)
    return

# Call the main() function to begin
# the program.
if __name__ == '__main__':
    # Define commandline parameters
    parser = argparse.ArgumentParser(
        description="Creates a zip application from the specified python script",
        formatter_class=RawTextHelpFormatter,
        epilog="""
        Usage Examples:
        Suppose you want to bundle in your python script dependencies
        Assume you store these modules under a folder named 'lib'
        You can easily create your zip app as follows:

        mkdir lib
        pip install -t lib -r requirements.txt
        make-zipapp -f myscript.py

        By default, the program will bundle in anything located in the local 'lib' folder
        
        You can also specify multiple dependencies, folders or files, as follows:

        make-zipapp -f myscript.py -d lib conf config.ini
        """,
        fromfile_prefix_chars='@')
    parser.add_argument(
        "-f",
        "--file",
        help="Specify the target python script",
        metavar="ARG", required=True)
    parser.add_argument(
        "-d",
        "--dependencies",
        help="Specify a list of dependencies to bundle in with the specified python script",
        required=False, nargs='*', default=['lib'])
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)