from django.contrib import admin

from .models import Form, Question, Option, Submission, Answer


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

    fields = (
        'title',
        'field_type',
        'required',
        'order',
    )

    ordering = (
        'order',
    )


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'created_by',
        'is_active',
        'created_at',
        'updated_at',
    )

    list_filter = (
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'description',
        'created_by__username',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
    )

    inlines = [
        QuestionInline,
    ]


class OptionInline(admin.TabularInline):
    model = Option
    extra = 1

    fields = (
        'title',
        'order',
    )

    ordering = (
        'order',
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'form',
        'field_type',
        'required',
        'order',
    )

    list_filter = (
        'field_type',
        'required',
        'form',
    )

    search_fields = (
        'title',
        'form__title',
    )

    ordering = (
        'form',
        'order',
    )

    autocomplete_fields = (
        'form',
    )

    inlines = [
        OptionInline,
    ]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'question',
        'order',
    )

    search_fields = (
        'title',
        'question__title',
    )

    ordering = (
        'question',
        'order',
    )

    autocomplete_fields = (
        'question',
    )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'form',
        'user',
        'created_at',
    )

    list_filter = (
        'form',
        'created_at',
    )

    search_fields = (
        'form__title',
        'user__username',
    )

    readonly_fields = (
        'created_at',
    )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'submission',
        'question',
        'short_answer',
    )

    search_fields = (
        'text_value',
        'question__title',
        'submission__form__title',
    )

    autocomplete_fields = (
        'submission',
        'question',
    )

    def short_answer(self, obj):
        if obj.text_value:
            return obj.text_value[:80]

        if obj.file_value:
            return obj.file_value.name

        return '-'

    short_answer.short_description = 'پاسخ'