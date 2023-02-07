#!/usr/bin/env python3
import subprocess
from github import Github
from datetime import datetime, timedelta
import argparse

from config import *
from helpers import *

ARGS = None

def parse_args():
    """ parse command line args, using argparse """
    parser = argparse.ArgumentParser(description="Lica is a somewhat configurable tool for analysing Linux kernel commits.")
    parser.add_argument("--since", nargs='?', type=int, default=20,
                        help="How many days back to search commit history?")
    parser.add_argument("--release", nargs='?', type=str, default="latest",
                        help="Which kernel release to analyse? Major.Minor E.g. latest, '6.1', '5.15' etc.")
    parser.add_argument("--backports", nargs='?', type=str,
                        help="Do you want to check to see if commits were backported? See config.py's 'coverage_list' config for details.")
    parser.add_argument("--token", nargs='?', type=str, default="",
                        help="Specify your GitHub API token for increased limits.")
    parser.add_argument("--repo", nargs='?', type=str, default="gregkh/linux",
                        help="Specify the GitHub repository you'd like to query over the API (only tested for gregkh/linux)")
    # XXX: outfile + format
    # XXX: granularity for filter by fix?
    # XXX: specify cache path
    # XXX: option to use local linux repo rather than api
    return parser.parse_args()


def get_commits(release=None, since=None):
    """ wip """
    since = datetime.now() -  timedelta(days=since)
    repo = Github(ARGS.token).get_repo(ARGS.repo)

    if release == "latest" or not release:
        branch = "master"
    elif release:
        branch = "linux-" + release + ".y"

    commits = repo.get_commits(sha=branch, since=since) # since
    return commits


def filter_commits(commits):
    """ wip """
    res = []
    threshold = 0.1
    total = commits.totalCount
    global STATS, ARGS

    print(f"|---- Filtering {total} commits\n|---- ", end='')
    for commit in commits:
        STATS["commits"] += 1

        if not filter_title(CONFIG, get_commit_title(commit)):
            continue
        if any(hit in get_commit_title(commit) for hit in ["Merge", "Revert"]):
            continue
        STATS["fixes"] += 1

        hits = filter_commit(CONFIG, commit)
        if not hits:
            continue
        STATS["filtered"] += 1

        reporter = get_commit_reporter(commit.commit.message)
        CVEs = get_commit_cves(commit.commit.message) # enough to not check title?

        if not filter_reporter(CONFIG, reporter):
            continue

        if ARGS.backports:
            files = commit.files
        else:
            files = None

        res.append({
            "sha": commit.sha,
            "module": get_commit_module(commit),
            "title": get_commit_title(commit),
            "message": commit.commit.message,
            "reporter": reporter,
            "cves": ",".join(list(dict.fromkeys(CVEs))), # remove duplicates
            "hits": list(dict.fromkeys(hits)), # remove duplicates
            "files": files,
            "coverage": "N/A"
        })

        if (STATS["commits"] / total) > threshold:
            print(f"{threshold*100:.0f}%...", end='')
            threshold += 0.1

    print('')
    return res


def get_coverage(fcommits):
    """ wip """
    for commit in fcommits:
        coverage = []
        skip = False

        for change in commit["files"]:
            changes = parse_patch(change.patch)
            for kvers in CONFIG["coverage_list"]:
                if not file_has_changes(kvers, change.filename, changes):
                    skip = True
                    break
                coverage.append(kvers.split('/')[-1]) # remove path, just folder name for stats
            if skip:
                break

        if coverage and not skip:
            commit["coverage"] = ", ".join(list(dict.fromkeys(coverage)))


def parse_stats(fcommits):
    """ wip """
    global STATS

    for cat in CONFIG["message_filter"]:
        STATS["hits"][cat] = 0

    for com in fcommits:
        module = com["module"].split('/')[0].split(',')[0]

        if module not in STATS["modules"]:
            STATS["modules"][module] = 1
        else:
            STATS["modules"][module] += 1

        if com["reporter"]:
            STATS["reported"] += 1

        if com["cves"]:
            STATS["cves"] += 1

        parse_filter_hits(CONFIG, STATS, com["hits"])

    STATS["modules"] = dict(sorted(STATS["modules"].items(), key=lambda item: item[1], reverse=True))
    STATS["hits"] = dict(sorted(STATS["hits"].items(), key=lambda item: item[1], reverse=True))



def print_commits(fcommits):
    """ wip """
    print(f"\n{'Commit':.<12} | {'Module':.<18} | {'Hits':.<60} | {'CVE':.<16} | {'Reporter':.<50} | {'Coverage':.<15}")
    print("-"*186)

    for com in fcommits:
        sha = com["sha"][:12]
        hits = ",".join(com["hits"])[:57]
        print(f"{sha:<12} | {com['module']:<18} | {hits:.<60} | {com['cves']:<16} | {com['reporter']:<50} | {com['coverage']:<15}")

    print("-"*186)


def print_stats():
    """ wip """
    global STATS

    print("Now For The Stats...")
    print("-"*186)

    print(f"[+] {STATS['filtered']} commits where matched from {STATS['fixes']} fixes, over {STATS['commits']} commits.")
    print(f"[+] {STATS['reported']} / {STATS['filtered']} listed a reporter.")
    print(f"[+] {STATS['cves']} / {STATS['filtered']} mentioned a CVE.")

    print(f"[+] Breakdown by category:")
    for cat in STATS["hits"]:
        print(f"|---- {cat}: {STATS['hits'][cat]}")

    print(f"[+] Breakdown by module:")
    for module in STATS["modules"]:
        print(f"|---- {module}: {STATS['modules'][module]}")


def main():
    global ARGS

    print_banner()
    ARGS = parse_args()

    print("[+] Fetching commits from GitHub API...")
    commits = get_commits(ARGS.release, ARGS.since)
    print("[+] Filtering commits based on config.py, this may involve some more API calls...")
    fcommits = filter_commits(commits)

    if ARGS.backports:
        print("[+] Scanning kernels to see if patches have been backported...")
        get_coverage(fcommits)

    parse_stats(fcommits)

    print_commits(fcommits)
    print_stats()

if __name__ == "__main__":
    main()
