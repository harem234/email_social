from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class CustomUserTestCase(TestCase):

    def test_create_user(self):
        """
        test creating normal user using manager

        """
        user = User.objects.create_user(email='normal@user.com', password='foo')

        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        self.assertEqual(user.site_id, 1)
        self.assertEqual(user.isEmailVerified, False)

        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass

        with self.assertRaises(TypeError):
            User.objects.create_user()

        with self.assertRaises(TypeError):
            User.objects.create_user(email='')

        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password="foo")

    def test_create_superuser(self):

        admin_user = User.objects.create_superuser(email='super@user.com', password='foo')
        self.assertEqual(admin_user.email, 'super@user.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username is None for the AbstractUser option
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='super@user.com', password='foo', is_superuser=False
            )

    def test_change_password(self):

        password = 'fooboo2@1!##r43df'
        user = User.objects.create_user(
            email='normal2@user.com',
            password=password,
        )

        self.assertTrue(user.check_password(password))

    def test_verify_email(self):
        """
        send email by user's sign up or user request to verify
        then verify request by clicking the link sent to email
        """
        pass

    def test_change_email(self):
        """
        send email if signed-in user request so
        then verify request by clicking the link and no other user exist with that user
        then ch

        """
        pass

    def test_forgot_email(self):
        """


        """
        pass

    def test_forgot_email(self):
        """


        """
        pass
