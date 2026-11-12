#!/usr/bin/env python3
"""Fail closed unless a release tag is SemVer, signed, on main, licensed, and changelogged."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-rc\.[1-9][0-9]*)?$")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def fail(message: str) -> int:
    print(f"::error::{message}")
    return 1


def main() -> int:
    tag = os.environ.get("GITHUB_REF_NAME", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GH_TOKEN", "")
    if not tag.startswith("v") or not VERSION.fullmatch(tag[1:]):
        return fail(f"Tag {tag!r} is not vMAJOR.MINOR.PATCH or vMAJOR.MINOR.PATCH-rc.N.")
    if not repo or not token:
        return fail("GITHUB_REPOSITORY or GH_TOKEN is unavailable.")

    version = tag[1:]
    ref = f"refs/tags/{tag}"
    try:
        if run("git", "cat-file", "-t", ref) != "tag":
            return fail("Release tag must be annotated; lightweight tags are forbidden.")
        tag_object = run("git", "rev-parse", f"{ref}^{{tag}}")
        commit = run("git", "rev-parse", f"{ref}^{{commit}}")
    except subprocess.CalledProcessError as exc:
        return fail(f"Unable to resolve an annotated tag object: {exc.output}")

    api_url = f"https://api.github.com/repos/{repo}/git/tags/{tag_object}"
    request = Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            tag_data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        return fail(f"Could not verify tag signature through GitHub API: {exc}")

    verification = tag_data.get("verification") or {}
    if verification.get("verified") is not True or verification.get("reason") != "valid":
        return fail(
            "GitHub does not report a valid cryptographic signature for this tag "
            f"(reason={verification.get('reason')!r})."
        )

    try:
        run("git", "fetch", "--no-tags", "origin", "+refs/heads/main:refs/remotes/origin/main")
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", commit, "refs/remotes/origin/main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return fail("The release commit is not reachable from origin/main.")

    if not any(Path(name).is_file() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt")):
        return fail("No LICENSE file exists. Choose and commit an explicit distribution license before releasing.")

    changelog = Path("CHANGELOG.md")
    if not changelog.is_file():
        return fail("CHANGELOG.md is missing.")
    text = changelog.read_text(encoding="utf-8")
    heading = re.compile(
        rf"^##\s+(?:\[v?{re.escape(version)}\]|v?{re.escape(version)})(?=\s|$)",
        re.MULTILINE | re.IGNORECASE,
    )
    if not heading.search(text):
        return fail(f"CHANGELOG.md must contain a release heading for {version}.")

    print(
        f"Release preflight passed: {tag}, annotated + GitHub-verified signature, "
        "main ancestry, explicit license, and versioned changelog."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
