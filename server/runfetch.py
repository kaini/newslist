#!/usr/bin/env python3
import sys
from newslist.database import fetch

if __name__ == "__main__":
    fetch(sys.argv[1])
