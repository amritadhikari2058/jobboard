from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_state(context, namespace, url_name, css_class="active"):
    """Return the active-page state for a sidebar/nav entry.

    Lets an include stay a single line instead of three: it gets the CSS
    class and the ``aria-current`` value together.
    """
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    is_active = (
        match is not None
        and match.namespace == namespace
        and match.url_name == url_name
    )
    return {
        "css": css_class if is_active else "",
        "current": "page" if is_active else "",
        "active": is_active,
    }


STATUS_META = {
    "pending": ("Pending", "bi-hourglass-split", "jb-status-pending"),
    "accepted": ("Accepted", "bi-check-circle-fill", "jb-status-accepted"),
    "rejected": ("Rejected", "bi-x-circle-fill", "jb-status-rejected"),
    "withdrawn": ("Withdrawn", "bi-dash-circle", "jb-status-withdrawn"),
}


@register.filter
def split(value, separator=","):
    """Split a free-text field into a clean list for tag rendering.

    Skills are stored as one comma separated string, which templates cannot
    iterate on directly.
    """
    if not value:
        return []
    return [part.strip() for part in str(value).split(separator) if part.strip()]


@register.simple_tag
def application_status(value):
    """Map an ``Application.status`` value to its label, icon and colour.

    Usage::

        {% application_status application.status as status %}
        <span class="jb-status {{ status.css }}">
            <i class="bi {{ status.icon }}" aria-hidden="true"></i>{{ status.label }}
        </span>

    Every state carries an icon and a word, so the meaning survives
    greyscale, high-contrast mode and colour blindness.
    """
    label, icon, css = STATUS_META.get(value, ("Unknown", "bi-question-circle", "jb-status-withdrawn"))
    return {"label": label, "icon": icon, "css": css}
