from django.contrib import admin

from testapp.models import User, Test, Response, Option, Submission, Question

# Register your models here.
admin.site.register(User)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Submission)
admin.site.register(Response)