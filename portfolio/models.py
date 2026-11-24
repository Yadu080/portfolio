"""Content models for the portfolio.

Everything a visitor sees is stored here and editable from /admin,
so the site can grow without touching templates or code.
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Orderable(models.Model):
    order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers appear first."
    )

    class Meta:
        abstract = True
        ordering = ["order", "pk"]


# --------------------------------------------------------------------------
# Site-wide settings (a single row)
# --------------------------------------------------------------------------
class SiteProfile(models.Model):
    full_name = models.CharField(max_length=120, default="Yadunandan M Nimbalkar")
    hero_first_line = models.CharField(
        max_length=40, default="Yadunandan",
        help_text="First line of the giant name in the hero.",
    )
    hero_second_line = models.CharField(
        max_length=40, default="Nimbalkar",
        help_text="Second line of the giant name in the hero.",
    )
    role = models.CharField(max_length=120, default="AI / ML Engineer")
    statement = models.CharField(
        max_length=200,
        default="I build AI systems that show their work.",
        help_text="Hero statement. Wrap words in *asterisks* to set them in italic serif.",
    )
    manifesto = models.TextField(
        help_text="The large editorial paragraph under the hero. *Asterisks* = italic accent.",
        blank=True,
    )
    bio = models.TextField(blank=True, help_text="Short bio used in the footer and meta tags.")
    location = models.CharField(max_length=80, default="Bengaluru, India")
    timezone = models.CharField(max_length=60, default="Asia/Kolkata")
    currently = models.CharField(
        max_length=160, blank=True,
        default="B.E. Computer Science (AI & ML), Global Academy of Technology — class of 2027",
    )
    open_to_work = models.BooleanField(default=True)
    availability_text = models.CharField(
        max_length=120, default="Open to AI Engineer & Data Scientist roles"
    )
    email = models.EmailField(blank=True)
    github_username = models.CharField(
        max_length=60, default="Yadu080",
        help_text="Used by 'Import from GitHub' in the Projects admin.",
    )
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    resume = models.FileField(upload_to="resume/", blank=True, help_text="PDF shown as 'Résumé'.")
    portrait = models.ImageField(upload_to="profile/", blank=True)
    closing_heading = models.CharField(
        max_length=160, default="Let's build something that *shows its work.*"
    )
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Site profile"
        verbose_name_plural = "Site profile"

    def __str__(self):
        return "Site profile"

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Stat(Orderable):
    value = models.CharField(max_length=24, help_text="e.g. 8.83 or Top 20")
    label = models.CharField(max_length=80)
    note = models.CharField(max_length=140, blank=True)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return f"{self.value} — {self.label}"


# --------------------------------------------------------------------------
# Projects
# --------------------------------------------------------------------------
class Project(Orderable):
    CATEGORY_CHOICES = [
        ("ml", "Machine Learning"),
        ("genai", "Generative AI / LLMs"),
        ("health", "AI for Health"),
        ("data", "Data & Decision Systems"),
        ("security", "ML Security"),
        ("fullstack", "Full-stack & Automation"),
        ("coursework", "Coursework"),
    ]
    COVER_STYLES = [
        ("constellation", "Constellation (points + links)"),
        ("waves", "Waves"),
        ("grid", "Grid field"),
        ("rings", "Rings"),
        ("bars", "Signal bars"),
    ]

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    kicker = models.CharField(
        max_length=200, blank=True, help_text="One-line pitch shown under the title."
    )
    summary = models.TextField(blank=True, help_text="Two or three sentences for cards and lists.")
    body = models.TextField(
        blank=True, help_text="Full case study. Markdown is supported (## headings, **bold**, lists, links)."
    )
    year = models.PositiveIntegerField(default=2026)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="ml")
    role = models.CharField(max_length=80, blank=True, help_text="e.g. Solo build, Team of 3")
    context = models.CharField(
        max_length=140, blank=True, help_text="e.g. IBM Z Datathon 2026"
    )
    stack = models.CharField(
        max_length=300, blank=True, help_text="Comma-separated, e.g. Python, PyTorch, FastAPI"
    )
    repo_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    extra_url = models.URLField(blank=True)
    extra_label = models.CharField(max_length=40, blank=True, default="Read more")
    cover = models.ImageField(
        upload_to="projects/", blank=True,
        help_text="Optional. Without one, a generative cover is drawn in the chosen style.",
    )
    cover_style = models.CharField(max_length=20, choices=COVER_STYLES, default="constellation")
    featured = models.BooleanField(default=False, help_text="Show in 'Selected work'.")
    published = models.BooleanField(default=True)
    # Synced from GitHub
    github_repo = models.CharField(max_length=140, blank=True, help_text="owner/name")
    language = models.CharField(max_length=40, blank=True)
    stars = models.PositiveIntegerField(default=0)
    pushed_at = models.DateTimeField(null=True, blank=True)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:120] or "project"
            slug, n = base, 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project", args=[self.slug])

    @property
    def stack_list(self):
        return [s.strip() for s in self.stack.split(",") if s.strip()]


class ProjectMetric(Orderable):
    project = models.ForeignKey(Project, related_name="metrics", on_delete=models.CASCADE)
    value = models.CharField(max_length=24)
    label = models.CharField(max_length=120)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return f"{self.value} {self.label}"


class ProjectImage(Orderable):
    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=200, blank=True)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return self.caption or self.image.name


# --------------------------------------------------------------------------
# Record: achievements, certifications, education, volunteering
# --------------------------------------------------------------------------
class Achievement(Orderable):
    KIND_CHOICES = [
        ("award", "Award / Ranking"),
        ("hackathon", "Hackathon / Datathon"),
        ("program", "Program"),
        ("leadership", "Leadership"),
    ]
    headline = models.CharField(
        max_length=40, blank=True, help_text="Big figure, e.g. 'Top 20'. Optional."
    )
    title = models.CharField(max_length=160)
    organization = models.CharField(max_length=140, blank=True)
    year = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="hackathon")
    highlight = models.BooleanField(default=False, help_text="Show as a large feature.")
    link = models.URLField(blank=True)
    project = models.ForeignKey(
        Project, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Optional related project.",
    )

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return self.title


class Certification(Orderable):
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=120)
    issued = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)
    skills = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["order", "-issued", "pk"]

    def __str__(self):
        return f"{self.title} — {self.issuer}"


class TimelineEntry(Orderable):
    KIND_CHOICES = [
        ("education", "Education"),
        ("experience", "Experience"),
        ("volunteering", "Volunteering"),
    ]
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="education")
    title = models.CharField(max_length=160)
    organization = models.CharField(max_length=160)
    period = models.CharField(max_length=60, help_text="e.g. 2023 — 2027")
    detail = models.CharField(max_length=120, blank=True, help_text="e.g. CGPA 8.83")
    description = models.TextField(blank=True)

    class Meta(Orderable.Meta):
        verbose_name_plural = "Timeline entries"

    def __str__(self):
        return f"{self.title}, {self.organization}"


class SkillGroup(Orderable):
    name = models.CharField(max_length=80)
    skills = models.TextField(help_text="Comma-separated list.")
    in_marquee = models.BooleanField(
        default=False, help_text="Also scroll these in the large moving type band."
    )

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return self.name

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]
