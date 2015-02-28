"""
Print the current process id and the script arguments on separate lines in
an output file.  Used for testing.
"""

import os
import sys

with open('stdout.txt', 'w') as out:
    print >>out, os.getpid()
    for arg in sys.argv:
        print >>out, arg
