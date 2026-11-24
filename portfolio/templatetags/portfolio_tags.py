import re

import markdown as md
from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

_EM = re.compile(r"\*(.+?)\*")


@register.filter
def accent(value: str):
    """Escape text, then turn *words* into <em> (rendered as italic serif)."""
    escaped = conditional_escape(value or "")
    return mark_safe(_EM.sub(r"<em>\1</em>", escaped))


@register.filter
def markdown(value: str):
    # Content is authored by the site owner in the admin; raw HTML is escaped.
    html = md.markdown(
        conditional_escape(value or ""),
        extensions=["extra", "sane_lists", "smarty"],
    )
    return mark_safe(html)


@register.filter
def pad2(value):
    try:
        return f"{int(value):02d}"
    except (TypeError, ValueError):
        return value


@register.filter
def words(value: str):
    """Split a string into words for per-word reveal animations."""
    return (value or "").split()
