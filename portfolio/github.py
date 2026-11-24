"""Minimal GitHub REST client (standard library only).

Set GITHUB_TOKEN in the environment to raise the anonymous rate limit
(60 requests/hour) — it is optional for a public profile.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime

from django.utils.dateparse import parse_datetime

API = "https://api.github.com"


class GitHubError(RuntimeError):
    pass


@dataclass
class Repo:
    full_name: str
    name: str
    description: str
    html_url: str
    homepage: str
    language: str
    stars: int
    fork: bool
    topics: list[str]
    pushed_at: datetime | None


def _get(path: str):
    req = urllib.request.Request(
        API + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "portfolio-site",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:  # pragma: no cover - network
        raise GitHubError(f"GitHub returned {exc.code} for {path}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network
        raise GitHubError(f"Could not reach GitHub: {exc.reason}") from exc


def fetch_repos(username: str) -> list[Repo]:
    repos: list[Repo] = []
    page = 1
    while True:
        batch = _get(f"/users/{username}/repos?per_page=100&page={page}&sort=pushed")
        if not batch:
            break
        for r in batch:
            repos.append(
                Repo(
                    full_name=r["full_name"],
                    name=r["name"],
                    description=r.get("description") or "",
                    html_url=r["html_url"],
                    homepage=r.get("homepage") or "",
                    language=r.get("language") or "",
                    stars=r.get("stargazers_count", 0),
                    fork=r.get("fork", False),
                    topics=r.get("topics") or [],
                    pushed_at=parse_datetime(r["pushed_at"]) if r.get("pushed_at") else None,
                )
            )
        if len(batch) < 100:
            break
        page += 1
    return repos


def pretty_title(name: str) -> str:
    """'Two-Tower_Recommendation_System' -> 'Two Tower Recommendation System'."""
    words = name.replace("_", " ").replace("-", " ").split()
    return " ".join(w if w.isupper() else w[:1].upper() + w[1:] for w in words)
