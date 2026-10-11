
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate using either username or email."""

    def authenticate(
        self,
        request,
        username=None,
        password=None,
        **kwargs,
    ):
        UserModel = get_user_model()
        identifier = username or kwargs.get(UserModel.USERNAME_FIELD)

        if not identifier or password is None:
            return None

        identifier = identifier.strip()

        try:
            user = UserModel._default_manager.get(
                Q(username__iexact=identifier)
                | Q(email__iexact=identifier)
            )
        except (
            UserModel.DoesNotExist,
            UserModel.MultipleObjectsReturned,
        ):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
