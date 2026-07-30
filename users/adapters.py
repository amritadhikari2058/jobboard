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
            user.save(update_fields=["role"])

        return user