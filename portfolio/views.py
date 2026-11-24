from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import (
    Achievement,
    Certification,
    Project,
    ProjectMetric,
    SiteProfile,
    SkillGroup,
    Stat,
    TimelineEntry,
)


def _projects():
    return Project.objects.filter(published=True).prefetch_related(
        Prefetch("metrics", queryset=ProjectMetric.objects.order_by("order", "pk"))
    )


def home(request):
    projects = list(_projects())
    archive = sorted(projects, key=lambda p: (-p.year, p.order, p.pk))
    categories = []
    for p in archive:
        pair = (p.category, p.get_category_display())
        if pair not in categories:
            categories.append(pair)
    skill_groups = list(SkillGroup.objects.all())
    marquee = [s for g in skill_groups if g.in_marquee for s in g.skill_list]
    context = {
        "profile": SiteProfile.load(),
        "stats": Stat.objects.all(),
        "featured": [p for p in projects if p.featured],
        "archive": archive,
        "categories": categories,
        "highlights": Achievement.objects.filter(highlight=True),
        "achievements": Achievement.objects.filter(highlight=False),
        "certifications": Certification.objects.all(),
        "education": TimelineEntry.objects.filter(kind="education"),
        "experience": TimelineEntry.objects.exclude(kind="education"),
        "skill_groups": skill_groups,
        "marquee": marquee,
    }
    return render(request, "portfolio/home.html", context)


def project_detail(request, slug):
    project = get_object_or_404(_projects().prefetch_related("images"), slug=slug)
    ordered = list(Project.objects.filter(published=True, featured=True)) or list(
        Project.objects.filter(published=True)
    )
    nxt = None
    if project in ordered:
        nxt = ordered[(ordered.index(project) + 1) % len(ordered)]
    elif ordered:
        nxt = ordered[0]
    if nxt == project:
        nxt = None
    return render(
        request,
        "portfolio/project.html",
        {"profile": SiteProfile.load(), "project": project, "next_project": nxt},
    )


def not_found(request, exception=None):
    return render(request, "portfolio/404.html", {"profile": SiteProfile.load()}, status=404)
