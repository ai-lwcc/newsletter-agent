from django import forms


class AICampaignCreateForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=False,
        help_text="Optional. If blank, AI will create a campaign title.",
    )

    pdf_attachment = forms.FileField(
        required=True,
        help_text="Upload the PDF that the AI should use to create the campaign.",
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
        help_text="If checked, Celery can send this campaign when the scheduled time arrives, but only after dry-run logs exist.",
    )