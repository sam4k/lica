#!/usr/bin/env python3
import pathlib

"""
Filter definitions.

This is my shoddy implementation for filtering commits base
on keywords:
- The key for the dictionary acts as a category,
used in statistcs,
- Each dictonary value is a list containing keywords you want
to filter for,
- Such that a commit containing (in title or body) any of the
keywords in any of the lists will be a hit

If the value is a list, the values are all concatenated into one ugly
regex to be matched against the commit text. For a string value, it's treated as
a sane regular expression and used that way (see filter_commit() in helpers.py)

If this is used in "message_filter" (see below), it will select
a commit containing keyword. However, if it's used in "message_ignore",
it will ignore the commit with any keyword.

Below are some super simple example to demonstrate some usecases for the filter
"system", they won't necessary generate useful results though.
"""
BASIC_FILTER = {
    "UAF": [ "use-after-free", "use after free", "UAF" ],
    "Double Free": [ "double-free", "double free" ],
    "Races": [ "race condition" ],
    "Heap Overflow": [ "heap overflow", "heap buffer overflow", "heap-based overflow", "heap-based buffer overflow" ],
    "Stack Overflow": [ "stack overflow", "stack buffer overflow", "stack-based overflow", "stack-based buffer overflow" ],
    "Memory Corruption": [ "out-of-bounds write", "oob write", "out of bounds write", "out-of-bound write", "out of bound write" ],
    "Info Leak": [ "info leak", "information leak", "uninitialised var",
                   "uinitialized var", "unititialised stack", "uninitialized stack",
                   "out-of-bounds read", "oob read", "out of bounds read", "out-of-bound read", "out of bound read"
    ],
    "General": [ "exploit", "memory corruption", "lpe ", "privesc", "privilege escalation", "attacker", "code execution", "hijack" ]
}

NUANCED_FILTER = {
    "Length": [ "check.*len", "len.*check", "missing.*len", "check.*size", "size.*check", "missing.*size" ],
    "Refs": [ "inc.*ref", "dec.*ref", "put.*ref", "forg.t.*ref" ],
    "Frees": [ "forg.t.*free", "missing.*free", "add.*free", "free.*cleanup", "cleanup.*free" ],
    "Validation": [ "missing.*validat", "forg.t.*validat", "add.*validat" ]
}


"""
Configuration definitions.

This configurations determines how Lica filters commits,
and any local kernel source trees you want to check for patches:
- @title_filter: regex used to intially filter commits by their title, done first
- @message_ignore: a filter dictionary (see above comment) by which to ignore commits on match,
  this is done before message_filter, so takes precedence
- @message_filter: a filter dictionary (see above comment) by which to accept commits on match,
- @reporter_filter: filter commits by a specific reporter (from Reported-By tag)
- @coverage_list: paths to kernel sources you want to compare commit patches against, this should be a path
  to a kernel source ROOT (containing mm/, net/, fs/ etc. etc.)

"""
DEF_CONFIG = {
    "title_filter": "(fix)",
    "message_ignore": None,
    "message_filter": BASIC_FILTER,
    "reporter_filter": None,
    "coverage_list": [
        #"/your/kernels/linux-5.15.90",
        #"/your/kernels/linux-5.10.165",
        #"/your/kernels/linux-5.4.230"
    ]
}

NUANCED_CONFIG = {
    "title_filter": "(fix)",
    "message_ignore": BASIC_FILTER,
    "message_filter": NUANCED_FILTER,
    "reporter_filter": None,
    "coverage_list": [
        #"/your/kernels/linux-5.15.90",
        #"/your/kernels/linux-5.10.165",
        #"/your/kernels/linux-5.4.230"
    ]
}

# this is the config you're gonna use
# XXX: should probs make this an arg or smth
CONFIG = DEF_CONFIG


# initing the stats here cos why not
STATS = {
    "commits": 0,
    "fixes": 0,
    "filtered": 0,
    "modules": {},
    "reported": 0,
    "cves": 0,
    "hits": {}
}
