from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SurvivorProfile, CounselorProfile, Counselor


class SurvivorProfileInline(admin.StackedInline):
    model = SurvivorProfile
    can_delete = False
    verbose_name_plural = 'Survivor Profile'


class CounselorProfileInline(admin.StackedInline):
    model = CounselorProfile
    can_delete = False
    verbose_name_plural = 'Counselor Profile'


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'user_type',
                    'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {
         'fields': ('first_name', 'last_name', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'survivor':
                return [SurvivorProfileInline]
            elif obj.user_type == 'counselor':
                return [CounselorProfileInline]
        return []


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SurvivorProfile)
admin.site.register(CounselorProfile)


@admin.register(Counselor)
class CounselorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'years_of_experience',
                    'expertise_sector')  # Display new fields
