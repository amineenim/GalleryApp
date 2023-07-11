from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator 

# define an EmailVerificationTokenGenerator class which generates token
# serving for email verification 
class EmailVerificationTokenGenerator(PasswordResetTokenGenerator) :
    def _make_hash_value(self, user, timestamp) :
        # customize the hash value generation 
        return str(user.id) + user.email + user.username + str(timestamp)
    