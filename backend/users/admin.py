from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'show_following')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')

    def show_following(self, obj):
        return obj.following.count()

    show_following.short_description = "Кол-во подписчиков"


admin.site.register(User, UserAdmin)
admin.site.register(Follow)
