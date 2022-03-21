from rest_framework.exceptions import NotFound, ValidationError
from reviews.models import ConfirmationCode, User


class ConfirmationCodeAuthBackend:
    def authenticate(self, request, username=None, confirmation_code=None):
        try:
            User.objects.get(username=username)
            code = ConfirmationCode.objects.get(
                user__username=username,
                code=confirmation_code
            )
        except User.DoesNotExist:
            raise NotFound('user not found')
        except ConfirmationCode.DoesNotExist:
            raise ValidationError(
                {'confirmation_code': 'invalid confirmation code'}
            )

        return code.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
