from django.contrib import admin

from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", "post", "author", "created")
    search_fields = ("text",)
    list_filter = ("created", "post", "author")
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    list_filter = ("user", "author")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
