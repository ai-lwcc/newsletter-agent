from django import forms


EMAIL_LENGTH_CHOICES = [
    ("short", "Short"),
    ("medium", "Medium"),
    ("long", "Long"),
]

TONE_CHOICES = [
    ("professional", "Professional"),
    ("warm", "Warm"),
    ("donor", "Donor Focused"),
    ("church", "Church / Community"),
]


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            return [
                single_file_clean(file, initial)
                for file in data
            ]

        return single_file_clean(data, initial)


class AICampaignCreateForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        help_text="Optional. If blank, AI will create a campaign title.",
    )

    attachments = MultipleFileField(
        required=True,
        widget=MultipleFileInput(
            attrs={
                "accept": ".pdf,.png,.jpg,.jpeg,.webp",
            }
        ),
        help_text=(
            "Upload one or more PDFs, posters, flyers, PNGs, JPGs, JPEGs, "
            "or WEBP files."
        ),
    )

    email_length = forms.ChoiceField(
        choices=EMAIL_LENGTH_CHOICES,
        initial="short",
        help_text="Control how detailed the AI-generated email should be.",
    )

    tone = forms.ChoiceField(
        choices=TONE_CHOICES,
        initial="professional",
        help_text="Choose the communication style for the AI-generated email.",
    )

    scheduled_send_time = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
            }
        ),
        help_text="Optional. Choose when this campaign should be sent.",
    )

    automatically_send_when_due = forms.BooleanField(
        required=False,
        help_text=(
            "If checked, Celery can send this campaign when the scheduled "
            "time arrives, but only after dry-run logs exist."
        ),
    )

    cover_link_url = forms.URLField(
        required=False,
        help_text="Optional Heyzine flipbook link.",
    )