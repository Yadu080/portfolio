from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html

from . import github
from .models import (
    Achievement,
    Certification,
    Project,
    ProjectImage,
    ProjectMetric,
    SiteProfile,
    SkillGroup,
    Stat,
    TimelineEntry,
)

admin.site.site_header = "Portfolio studio"
admin.site.site_title = "Portfolio studio"
admin.site.index_title = "Edit your site — changes go live on save"
admin.site.site_url = "/"


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Hero", {"fields": ["full_name", "hero_first_line", "hero_second_line", "role", "statement"]}),
        ("About", {"fields": ["manifesto", "bio", "currently", "location", "timezone"]}),
        ("Availability", {"fields": ["open_to_work", "availability_text"]}),
        ("Links & files", {"fields": ["email", "github_username", "github_url", "linkedin_url", "twitter_url", "resume", "portrait"]}),
        ("Closing & SEO", {"fields": ["closing_heading", "meta_description"]}),
    ]

    def has_add_permission(self, request):
        return not SiteProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteProfile.load()
        return HttpResponseRedirect(reverse("admin:portfolio_siteprofile_change", args=[obj.pk]))


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ["value", "label", "note", "order"]
    list_editable = ["order"]


class ProjectMetricInline(admin.TabularInline):
    model = ProjectMetric
    extra = 1
    fields = ["value", "label", "order"]


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ["image", "caption", "order"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    change_list_template = "admin/portfolio/project/change_list.html"
    list_display = ["title", "year", "category", "featured", "published", "order", "stars", "cover_thumb"]
    list_editable = ["featured", "published", "order"]
    list_filter = ["featured", "published", "category", "year"]
    search_fields = ["title", "kicker", "summary", "stack"]
    prepopulated_fields = {"slug": ["title"]}
    inlines = [ProjectMetricInline, ProjectImageInline]
    actions = ["refresh_from_github", "make_featured", "make_unfeatured"]
    fieldsets = [
        (None, {"fields": ["title", "slug", "kicker", "summary", "featured", "published", "order"]}),
        ("Details", {"fields": ["year", "category", "role", "context", "stack"]}),
        ("Links", {"fields": ["repo_url", "live_url", ("extra_url", "extra_label")]}),
        ("Cover", {"fields": ["cover", "cover_style"]}),
        ("Case study", {"fields": ["body"], "classes": ["wide"]}),
        ("GitHub (filled automatically)", {"fields": ["github_repo", "language", "stars", "pushed_at"], "classes": ["collapse"]}),
    ]

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        if obj.cover:
            return format_html('<img src="{}" style="height:32px;border-radius:3px">', obj.cover.url)
        return obj.get_cover_style_display()

    @admin.action(description="Show in Selected work")
    def make_featured(self, request, queryset):
        queryset.update(featured=True)

    @admin.action(description="Remove from Selected work")
    def make_unfeatured(self, request, queryset):
        queryset.update(featured=False)

    @admin.action(description="Refresh stars / language / last push from GitHub")
    def refresh_from_github(self, request, queryset):
        profile = SiteProfile.load()
        try:
            repos = {r.full_name.lower(): r for r in github.fetch_repos(profile.github_username)}
        except github.GitHubError as exc:
            self.message_user(request, str(exc), messages.ERROR)
            return
        updated = 0
        for project in queryset:
            repo = repos.get(project.github_repo.lower())
            if repo:
                project.stars = repo.stars
                project.language = repo.language
                project.pushed_at = repo.pushed_at
                project.save(update_fields=["stars", "language", "pushed_at"])
                updated += 1
        self.message_user(request, f"Refreshed {updated} project(s) from GitHub.")

    # ---- "Import from GitHub" screen ----------------------------------
    def get_urls(self):
        custom = [
            path(
                "import-github/",
                self.admin_site.admin_view(self.import_github_view),
                name="portfolio_project_import_github",
            )
        ]
        return custom + super().get_urls()

    def import_github_view(self, request):
        profile = SiteProfile.load()
        try:
            repos = github.fetch_repos(profile.github_username)
        except github.GitHubError as exc:
            self.message_user(request, str(exc), messages.ERROR)
            return HttpResponseRedirect(reverse("admin:portfolio_project_changelist"))

        known = {p.lower() for p in Project.objects.exclude(github_repo="").values_list("github_repo", flat=True)}
        known |= {u.rstrip("/").lower() for u in Project.objects.exclude(repo_url="").values_list("repo_url", flat=True)}

        def is_known(r):
            return r.full_name.lower() in known or r.html_url.lower() in known

        if request.method == "POST":
            chosen = set(request.POST.getlist("repo"))
            created = 0
            for r in repos:
                if r.full_name in chosen and not is_known(r):
                    Project.objects.create(
                        title=github.pretty_title(r.name),
                        summary=r.description,
                        kicker=r.description[:200],
                        stack=", ".join(filter(None, [r.language, *r.topics])),
                        repo_url=r.html_url,
                        live_url=r.homepage,
                        github_repo=r.full_name,
                        language=r.language,
                        stars=r.stars,
                        pushed_at=r.pushed_at,
                        year=r.pushed_at.year if r.pushed_at else 2026,
                        published=False,
                        order=500,
                    )
                    created += 1
            self.message_user(
                request,
                f"Imported {created} project(s) as drafts. Edit them, then tick 'Published' to show them on the site.",
            )
            return HttpResponseRedirect(reverse("admin:portfolio_project_changelist"))

        rows = [{"repo": r, "known": is_known(r)} for r in repos]
        context = {
            **self.admin_site.each_context(request),
            "title": f"Import from GitHub · @{profile.github_username}",
            "rows": rows,
            "opts": self.model._meta,
            "new_count": sum(1 for row in rows if not row["known"]),
        }
        return render(request, "admin/portfolio/project/import_github.html", context)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "year", "kind", "highlight", "order"]
    list_editable = ["highlight", "order"]
    list_filter = ["kind", "highlight"]


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ["title", "issuer", "issued", "order"]
    list_editable = ["order"]
    search_fields = ["title", "issuer"]


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "kind", "period", "order"]
    list_editable = ["order"]
    list_filter = ["kind"]


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "in_marquee", "order"]
    list_editable = ["in_marquee", "order"]
