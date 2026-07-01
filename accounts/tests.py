from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


User = get_user_model()


class AccountFlowTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_account',
            password='pass12345',
            email='admin@example.com',
            role='ADMIN',
        )
        self.owner = User.objects.create_superuser(
            username='owner_account',
            password='pass12345',
            email='owner@example.com',
            role='ADMIN',
        )
        self.student = User.objects.create_user(
            username='student_account',
            password='pass12345',
            email='student@example.com',
            role='STUDENT',
            student_id='SV100',
        )

    def test_register_logs_user_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'new_student',
            'email': 'new@example.com',
            'student_id': 'SV200',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        })

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='new_student').exists())

    def test_user_can_change_own_password(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse('password-change'), {
            'old_password': 'pass12345',
            'new_password1': 'NewStrongPass12345',
            'new_password2': 'NewStrongPass12345',
        })

        self.assertRedirects(response, reverse('account-settings'))
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password('NewStrongPass12345'))

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_forgot_password_request_reaches_done_page(self):
        response = self.client.post(reverse('password-reset'), {'email': self.student.email})

        self.assertRedirects(response, reverse('password-reset-done'))

    def test_admin_can_update_any_account_role_and_status(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-update', args=[self.student.pk]), {
            'username': self.student.username,
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': self.student.email,
            'role': 'LIBRARIAN',
            'student_id': self.student.student_id,
            'is_staff': 'on',
        })

        self.assertRedirects(response, reverse('admin-panel'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.role, 'LIBRARIAN')
        self.assertTrue(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)
        self.assertFalse(self.student.is_active)

    def test_regular_admin_cannot_grant_superuser_permission(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-update', args=[self.student.pk]), {
            'username': self.student.username,
            'first_name': self.student.first_name,
            'last_name': self.student.last_name,
            'email': self.student.email,
            'role': 'ADMIN',
            'student_id': self.student.student_id,
            'is_active': 'on',
            'is_staff': 'on',
            'is_superuser': 'on',
        })

        self.assertRedirects(response, reverse('admin-panel'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.role, 'ADMIN')
        self.assertTrue(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)

    def test_admin_can_reset_other_user_password(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-password-reset', args=[self.student.pk]), {
            'new_password1': 'AdminSetPass12345',
            'new_password2': 'AdminSetPass12345',
        })

        self.assertRedirects(response, reverse('admin-panel'))
        self.student.refresh_from_db()
        self.assertTrue(self.student.check_password('AdminSetPass12345'))

    def test_regular_admin_cannot_edit_highest_account(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('user-update', args=[self.owner.pk]))

        self.assertEqual(response.status_code, 403)

    def test_regular_admin_cannot_reset_highest_account_password(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('user-password-reset', args=[self.owner.pk]), {
            'new_password1': 'HackedPass12345',
            'new_password2': 'HackedPass12345',
        })

        self.assertEqual(response.status_code, 403)
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('pass12345'))

    def test_highest_account_can_edit_admin_account(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('user-update', args=[self.admin.pk]), {
            'username': self.admin.username,
            'first_name': self.admin.first_name,
            'last_name': self.admin.last_name,
            'email': self.admin.email,
            'role': 'ADMIN',
            'student_id': '',
            'is_active': 'on',
            'is_staff': 'on',
        })

        self.assertRedirects(response, reverse('admin-panel'))

    def test_student_cannot_access_user_management(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('admin-panel'))

        self.assertEqual(response.status_code, 403)
