import json

import ollama

from core.models import Group
from core.pdf_service import extract_text_from_pdf


AI_MODEL = "gemma3"


def generate_campaign_ai_draft(campaign):
    if not campaign.pdf_attachment:
        raise ValueError("Campaign must have a PDF attachment before generating AI draft.")

    pdf_text = extract_text_from_pdf(campaign.pdf_attachment.path)

    available_groups = list(
        Group.objects.values_list("name", flat=True)
    )

    prompt = f"""
You are helping create a newsletter campaign draft.

Read the PDF text and generate:
1. email_subject
2. email_body
3. whatsapp_message
4. suggested_groups
5. summary

Only suggest groups from this list:
{available_groups}

Return valid JSON only.

PDF text:
{pdf_text}
"""

    response = ollama.chat(
        model=AI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    content = response["message"]["content"]

    return json.loads(content)