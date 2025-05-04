from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model with email as the primary identifier
    and support for different user types.
    """
    USER_TYPE_CHOICES = (
        ('survivor', 'Survivor'),
        ('counselor', 'Counselor'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='survivor')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def is_survivor(self):
        return self.user_type == 'survivor'

    def is_counselor(self):
        return self.user_type == 'counselor'


class SurvivorProfile(models.Model):
    """
    Profile for Survivor users with additional fields.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='survivor_profile')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class CounselorProfile(models.Model):
    """
    Profile for Counselor users with additional fields.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='counselor_profile')
    license_number = models.CharField(max_length=100)
    specialization = models.CharField(max_length=200)
    bio = models.TextField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Assignment(models.Model):
    """
    Model for tracking counselor assignments to survivors with enhanced tracking
    and validation capabilities.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated')
    ]

    counselor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='counselor_assignments',
        limit_choices_to={'user_type': 'counselor'}
    )
    survivor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='survivor_assignments',
        limit_choices_to={'user_type': 'survivor'}
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the assignment")
    next_session_date = models.DateTimeField(null=True, blank=True)
    total_sessions = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Assignment: {self.counselor.username} - {self.survivor.username} ({self.status})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.counselor.user_type != 'counselor':
            raise ValidationError('Selected user must be a counselor.')
        if self.survivor.user_type != 'survivor':
            raise ValidationError('Selected user must be a survivor.')
        if self.counselor == self.survivor:
            raise ValidationError('Counselor and survivor cannot be the same user.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('counselor', 'survivor', 'status')
        ordering = ['-assigned_date', 'status']
        verbose_name = 'Counselor Assignment'
        verbose_name_plural = 'Counselor Assignments'
        permissions = [
            ('can_view_assignments', 'Can view assignments'),
            ('can_edit_assignments', 'Can edit assignments'),
            ('can_delete_assignments', 'Can delete assignments'),
            ('can_change_status', 'Can change assignment status'),
        ]
        indexes = [
            models.Index(fields=['status', 'assigned_date']),
            models.Index(fields=['counselor', 'status']),
            models.Index(fields=['survivor', 'status']),
        ]