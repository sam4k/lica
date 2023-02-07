# LInux Commit Analyser
This is a *hacky* little tool I wrote to parse Linux kernel commits, with security fixes in mind.

## Overview
Lica allows you to parse a Linux repository's commit history, filtering for fixes and looking for specific keywords.  

I've included some statistics in the output and a naive search for patch coverage if you give it some local kernel sources.  

I wrote more about the motivation behind this tool over on my blog, in the post [Analysing Linux Kernel Commits](https://sam4k.com).  


## Usage
The `--help` output details the available arguments, and should run out of the box with the `requirements.txt`:

``` 
$ python3 lica/core.py --help

          .____    .__
          |    |   |__| ____ _____
          |    |   |  |/ ___\\__  \
          |    |___|  \  \___ / __ \_
          |_______ \__|\___  >____  /
                  \/       \/     \/

                   - some kind of tool to analyse Linux kernel commits.
    
usage: core.py [-h] [--since [SINCE]] [--release [RELEASE]] [--backports [BACKPORTS]] [--token [TOKEN]]
               [--repo [REPO]]

Lica is a somewhat configurable tool for analysing Linux kernel commits.

options:
  -h, --help            show this help message and exit
  --since [SINCE]       How many days back to search commit history?
  --release [RELEASE]   Which kernel release to analyse? Major.Minor E.g. latest, '6.1', '5.15' etc.
  --backports [BACKPORTS]
                        Do you want to check to see if commits were backported? See config.py's
                        'coverage_list' config for details.
  --token [TOKEN]       Specify your GitHub API token for increased limits.
  --repo [REPO]         Specify the GitHub repository you'd like to query over the API (only tested for
                        gregkh/linux)
  
$ python3 core.py --token my_github_token --backports /mnt/black/Kernels/ --since 180
```


## Configuration
I aplogise in advance for this lol, but to configure Lica I went for a quick and dirty dictionary-based approach.

In `config.py` you can basically define your own dictionaries for filters and configurations. I've included comments for both the filter/keyword dictionaries and overarching configuration dictionary, as well as examples. Hopefully it's not too awkward.


## Github + Ratelimiting 
Okay, so long story short, initially I wrote this to manully parse the output of running `git log` on a local repository. Then I realised, oof, I might want to actually push this code. Surely there's a better way?  

Then I remembered APIs were a thing and lo and behold, GitHub has an API for just this. So I reimplemented everything using [PyGithub](https://github.com/PyGithub/PyGithub) only to find out not only is it slower but you can also get rate limited pretty easy without [setting up a token](https://github.com/settings/tokens).  

I played around briefly with trying to cache results (e.g. `requests_cache`), but didn't get anywhere. So if this gets any use I'll look more into that or just reimplement an option to just use a local repository to query.  


## Roadmap
I haven't spent a lot of time on this tool, but there's plenty of scope to improve and expand upon it. I'll chuck some ideas here.
- [ ] add comments

Contributions welcome are welcome!
