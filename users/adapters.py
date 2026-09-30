from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class GoogleSocialAccountAdapter(DefaultSocialAccountAdapter):

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        role = request.session.pop(
            "google_registration_role",
            None,
        )

        if role in ["normal_user", "recruiter"]:
            user.role = role

        extra = sociallogin.account.extra_data
        user.first_name = extra.get("given_name", "")
        user.last_name = extra.get("family_name", "")

        user.save()

        from .models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=user)
        picture_url = extra.get("picture")
        if picture_url and not profile.profile_pic:
            import urllib.request

            try:
                ext = "jpg"
                filename = f"google_{user.id}.{ext}"
                urllib.request.urlretrieve(
                    picture_url,
                    f"media/profile_pics/{filename}",
                )
                profile.profile_pic = f"profile_pics/{filename}"
                profile.save(update_fields=["profile_pic"])
            except Exception:
                pass

        return user