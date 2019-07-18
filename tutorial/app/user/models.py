from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractUser
)
# from rest_framework import generic

# Create your models here.

class User(AbstractUser):

    username = None
    email = models.EmailField(db_index=True, unique=True)
    first_name = models.CharField(max_length=255, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):

        return self.email

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.id,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')
        return token.decode('utf-8')

    def get_user(self, user_id):

        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            raise ValidationError(response['error']['user_exist'])
        return user

    def get_user_role(self, user_id):
        ''' get the user role '''

        user = User.objects.filter(id=user_id).first()
        return user

    def delete_user(self, user_id):
        user = User.objects.filter(id=user_id).first()
        user.is_active = False
        return user