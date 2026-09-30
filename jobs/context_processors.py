from notifications.models import Notification


def notification_count(request):
    if request.user.is_authenticated:
        unread_notification_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    else:
        unread_notification_count = 0
    return {"unread_notification_count": unread_notification_count}


def user_display(request):
    if not request.user.is_authenticated:
        return {"user_display_name": "", "user_avatar_url": ""}

    user = request.user
    name = user.get_full_name().strip()
    if not name:
        name = user.email

    avatar_url = ""
    if hasattr(user, "userprofile") and user.userprofile.profile_pic:
        avatar_url = user.userprofile.profile_pic.url
    else:
        if user.first_name:
            avatar_url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&background=0d6efd&color=fff&size=128"
        else:
            avatar_url = f"https://ui-avatars.com/api/?name={user.email[0].upper()}&background=0d6efd&color=fff&size=128"

    return {"user_display_name": name, "user_avatar_url": avatar_url}
