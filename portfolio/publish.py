"""Publish the site as static files to GitHub Pages.

The studio (Django admin) runs on your own computer. "Publish" renders every
public page to plain HTML, copies the CSS/JS/images next to it, and pushes the
result to the GitHub Pages repository (<username>.github.io by default).
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import RequestFactory

from . import views
from .models import Project, SiteProfile

SITE_REPO_DIR = Path(settings.BASE_DIR) / ".site-repo"


class PublishError(Exception):
    pass


def pages_repo():
    """'owner/name' of the GitHub Pages repository."""
    if getattr(settings, "PUBLISH_REPO", ""):
        return settings.PUBLISH_REPO
    user = (SiteProfile.load().github_username or "").strip()
    if not user:
        raise PublishError("Set your GitHub username in Site profile first.")
    return f"{user}/{user.lower()}.github.io"


def pages_url():
    owner, name = pages_repo().split("/", 1)
    if name.lower() == f"{owner.lower()}.github.io":
        return f"https://{name.lower()}/"
    return f"https://{owner.lower()}.github.io/{name}/"


def _write(path: Path, response):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(response.content)


def build_site(out: Path) -> int:
    """Render all public pages and assets into `out`. Returns the page count."""
    rf = RequestFactory(SERVER_NAME="localhost")
    _write(out / "index.html", views.home(rf.get("/")))
    pages = 1
    for project in Project.objects.filter(published=True):
        url = project.get_absolute_url()
        _write(out / url.strip("/") / "index.html", views.project_detail(rf.get(url), slug=project.slug))
        pages += 1
    _write(out / "404.html", views.not_found(rf.get("/404/")))

    # CSS, JS and fonts from the app (the admin's own files are not needed).
    static_root = out / settings.STATIC_URL.strip("/")
    for finder in finders.get_finders():
        for rel, storage in finder.list(["*.map", ".DS_Store"]):
            if rel.startswith("admin/"):
                continue
            dest = static_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            with storage.open(rel) as src:
                dest.write_bytes(src.read())

    media = Path(settings.MEDIA_ROOT)
    if media.exists():
        shutil.copytree(media, out / settings.MEDIA_URL.strip("/"), dirs_exist_ok=True)

    (out / ".nojekyll").write_text("")
    return pages


def _git(*args, cwd=SITE_REPO_DIR):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        raise PublishError((result.stderr or result.stdout).strip() or f"git {args[0]} failed")
    return result.stdout.strip()


def publish() -> str:
    """Build and push. Returns a human-readable summary."""
    repo = pages_repo()
    remote = f"https://github.com/{repo}.git"
    if not (SITE_REPO_DIR / ".git").exists():
        if SITE_REPO_DIR.exists():
            shutil.rmtree(SITE_REPO_DIR)
        _git("clone", "--depth", "1", remote, str(SITE_REPO_DIR), cwd=settings.BASE_DIR)
    else:
        _git("fetch", "--depth", "1", "origin")
        _git("reset", "--hard", "origin/HEAD")

    for child in SITE_REPO_DIR.iterdir():
        if child.name in (".git", "CNAME"):
            continue
        shutil.rmtree(child) if child.is_dir() else child.unlink()

    pages = build_site(SITE_REPO_DIR)
    _git("add", "-A")
    if not _git("status", "--porcelain"):
        return f"Nothing changed since the last publish. Live at {pages_url()}"
    stamp = datetime.now().strftime("%d %b %Y, %H:%M")
    _git(
        "-c", "user.name=Portfolio studio",
        "-c", "user.email=studio@users.noreply.github.com",
        "commit", "-m", f"Publish {stamp}",
    )
    _git("push", "origin", "HEAD")
    return f"Published {pages} pages. Live at {pages_url()} in about a minute."


def last_published():
    if not (SITE_REPO_DIR / ".git").exists():
        return None
    try:
        return _git("log", "-1", "--format=%cd", "--date=format:%d %b %Y, %H:%M")
    except PublishError:
        return None
