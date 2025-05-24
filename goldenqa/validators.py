import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Password must contain at least one letter and one number."),
                code='password_no_alphanum',
            )

    def get_help_text(self):
        return _("Your password must contain at least one letter and one number.") 