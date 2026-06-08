import json
import os
import re

import ollama

from core.models import Group
from core.pdf_service import extract_text_from_pdf



AI_MODEL = os.getenv(
    "AI_MODEL",
    "llama3.1:8b-instruct-q4_K_M"
)

def extract_json_from_text(text):
    """
    Extract JSON even if the model wraps it in markdown or explanation text.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        raise ValueError(f"AI did not return JSON. Response was: {text[:500]}")

    return json.loads(match.group(0))


def generate_campaign_ai_draft(campaign):
    if not campaign.pdf_attachment:
        raise ValueError(
            "Campaign must have a PDF attachment before generating AI draft."
        )

    pdf_text = extract_text_from_pdf(campaign.pdf_attachment.path)

    print("\n========== PDF LENGTH ==========")
    print(len(pdf_text))
    print("================================\n")
    print("\n========== PDF PREVIEW ==========")
    print(pdf_text[:1000])
    print("=================================\n")

    available_groups = list(
        Group.objects.values_list("name", flat=True)
    )

    prompt = f"""
You are an experienced nonprofit communications assistant.

Your job is NOT to summarize the entire PDF in detail.

Your job is to write a SHORT email message that will be sent together with the attached PDF.

The PDF itself will be attached to the email, so the email body should only briefly introduce the attachment and encourage the reader to open it.

Return ONLY valid JSON.

Do not return markdown.
Do not return explanations.
Do not return comments.
Do not return ```json.
Do not return any text before or after the JSON.

The JSON MUST match this exact structure:

{{
  "email_subject": "",
  "email_body": "",
  "whatsapp_message": "",
  "suggested_groups": [],
  "summary": ""
}}

AVAILABLE GROUPS:
{available_groups}

WRITING RULES:

1. email_subject:
   - Short and professional.
   - Maximum 12 words.

2. email_body:
   - Short accompanying email.
   - 2 to 4 short paragraphs only.
   - Do not restate the whole PDF.
   - Do not list every section of the PDF.
   - Mention that the full PDF is attached.
   - Include only 1 to 3 key highlights from the PDF.
   - Use a warm, professional nonprofit tone.
   - End with:
     Living Water Counselling Centre

3. whatsapp_message:
   - Maximum 500 characters.
   - Short message that tells people the PDF/report/newsletter is attached or available by email.
   - Do not include too much detail.

4. summary:
   - Internal summary only.
   - Maximum 3 sentences.
   - Describe what the PDF is about.

5. suggested_groups:
   - Choose only from AVAILABLE GROUPS.
   - Select groups that would reasonably need to receive this PDF.
   - If the PDF is an annual report, prioritize supporters, sponsors, donors, church partners, board members, volunteers, and general newsletter groups if those exist.
   - If no clear match exists and "General Newsletter" exists, use ["General Newsletter"].
   - Never invent group names that are not in AVAILABLE GROUPS.

IMPORTANT:
The email should sound like it is accompanying an attachment, not replacing the attachment.

PDF CONTENT:
{pdf_text[:8000]}
"""

    response = ollama.chat(
        model=AI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a JSON API. "
                    "You must always return one valid JSON object only. "
                    "Do not return markdown. "
                    "Do not return explanation text."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
        options={
            "temperature": 0,
            "num_predict": 1200,
        },
    )

    content = response["message"]["content"]

    return extract_json_from_text(content)