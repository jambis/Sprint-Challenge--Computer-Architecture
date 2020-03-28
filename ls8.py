#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) > 1:  
    cpu.load(sys.argv[1])

    cpu.run()

else:
    print("Please provide a path to a program to load. Example: 'example/print.ls8'")