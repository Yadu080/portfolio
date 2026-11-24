# Yadunandan M Nimbalkar — Portfolio

A Django portfolio with a Three.js "latent space" hero, GSAP scroll motion and an
admin "studio" so every word, project, metric, certificate and image can be edited
without touching code.

**Live:** https://yadu080.github.io/ (GitHub Pages, published from the studio)

## Everyday editing (no code)

1. Double-click **Open Portfolio Studio.command** in this folder. The first time, it asks
   you to create a username and password for the studio.
2. Your browser opens the studio. Edit anything and save; check it at http://127.0.0.1:8000.
3. On the studio home page, press **Publish to the live site**. The public site updates in about a minute.

Publishing renders every page to plain HTML and pushes it to the `Yadu080/yadu080.github.io`
repository (change with `PORTFOLIO_PUBLISH_REPO=owner/name`). From a terminal:
`python manage.py publish_site`. Your content lives in `db.sqlite3` and `media/` on this
computer, so back that folder up.

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_portfolio      # loads GitHub + LinkedIn content (first run only)
python manage.py createsuperuser     # your login for the studio
python manage.py runserver
```

Site: http://127.0.0.1:8000 · Studio: http://127.0.0.1:8000/admin

## Editing without code (the studio at /admin)

| To change… | Go to |
|---|---|
| Hero name, statement, manifesto, availability, email, links, résumé PDF | **Site profile** |
| The four big numbers under the manifesto | **Stats** |
| Projects, their metrics, gallery images, case-study text | **Projects** |
| Rankings, hackathons, leadership | **Achievements** (tick *Highlight* for the big rows) |
| Licences & certifications | **Certifications** |
| Education and volunteering | **Timeline entries** |
| Toolkit and the moving type band | **Skill groups** |

Tips:
- Wrap words in `*asterisks*` in the statement, manifesto or closing heading to set them in the orange italic serif.
- Case studies accept Markdown (`## Heading`, `**bold**`, `- lists`, links).
- **Featured** puts a project in *Selected work*; **Order** controls position (lower = earlier).
- No cover image? Pick a **Cover style** and the site draws a unique generative cover for it.

### Adding new GitHub projects
Projects → **Import from GitHub** lists every public repo of the username in Site profile
that isn't on the site yet. Tick the ones you want: they arrive as drafts with description,
language, topics, stars and links filled in. Add metrics or a cover, tick **Published**, save.
The **Refresh stars / language** action re-syncs existing projects. Set `GITHUB_TOKEN` to
raise GitHub's anonymous rate limit (optional).

## Alternative: run it as a live Django server (e.g. Render, Railway)

- Build command: `./build.sh`
- Start command: `gunicorn config.wsgi`
- Environment: `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY=<long random string>`,
  `DJANGO_ALLOWED_HOSTS=yourdomain.com`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com`
- Content lives in SQLite and uploads in `media/`. Mount a persistent disk and point
  `DJANGO_DB_PATH` and `DJANGO_MEDIA_ROOT` at it so edits survive redeploys.

## Structure

```
config/                 settings, urls
portfolio/models.py     everything editable
portfolio/admin.py      the studio, incl. GitHub import
portfolio/management/commands/seed_portfolio.py   initial content
portfolio/templates/portfolio/   home, case study, 404
portfolio/static/portfolio/css/  site.css (tokens, hero, work) + sections.css
portfolio/static/portfolio/js/   latent.js (3D hero), site.js (motion), covers.js (generative covers)
seed_media/             original screenshots from the repos
```
