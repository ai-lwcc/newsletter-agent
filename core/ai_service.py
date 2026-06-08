import json
import os
import re

import ollama

from core.models import Group
from core.pdf_service import extract_text_from_pdf


AI_MODEL = os.getenv(
    "AI_MODEL",
    "llama3.1:8b-instruct-q4_K_M",
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


def get_email_length_rules(email_length):
    if email_length == "medium":
        return (
            "Write a medium-length email. "
            "Use 3 to 5 short paragraphs. "
            "Include 2 to 4 key highlights from the PDF."
        )

    if email_length == "long":
        return (
            "Write a longer newsletter-style email. "
            "Use 5 to 7 short paragraphs. "
            "Include several key highlights, but still do not replace the PDF."
        )

    return (
        "Write a short accompanying email. "
        "Use 2 to 4 short paragraphs only. "
        "Include only 1 to 3 key highlights from the PDF."
    )


def get_tone_rules(tone):
    if tone == "warm":
        return (
            "Use a warm, friendly, and appreciative tone. "
            "Make the message feel welcoming and human."
        )

    if tone == "donor":
        return (
            "Use a donor-focused tone. "
            "Emphasize gratitude, impact, generosity, and continued support."
        )

    if tone == "church":
        return (
            "Use a church and community-focused tone. "
            "Emphasize partnership, service, care, community, and shared mission."
        )

    return (
        "Use a professional nonprofit communication tone. "
        "Keep the message clear, polished, and respectful."
    )


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

    email_length = getattr(campaign, "email_length", "short")
    tone = getattr(campaign, "tone", "professional")

    email_length_rules = get_email_length_rules(email_length)
    tone_rules = get_tone_rules(tone)

    prompt = f"""
You are an experienced nonprofit communications assistant.

Your job is NOT to summarize the entire PDF in detail.

Your job is to write an email message that will be sent together with the attached PDF.

The PDF itself will be attached to the email, so the email body should introduce the attachment and encourage the reader to open it.

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
  "email_body_zh": "",
  "whatsapp_message": "",
  "suggested_groups": [],
  "summary": ""
}}

AVAILABLE GROUPS:
{available_groups}

USER SELECTED SETTINGS:

Email Length:
{email_length}

Tone:
{tone}

EMAIL LENGTH RULES:
{email_length_rules}

TONE RULES:
{tone_rules}

WRITING RULES:

1. email_subject:
   - Short and professional.
   - Maximum 12 words.

2. email_body:
   - This email is only an accompanying message for the attached PDF.
   - Do not restate the whole PDF.
   - Mention that the full PDF is attached.
   - Include only 1 to 3 key highlights from the PDF.
   - End with: Living Water Counselling Centre

3. Length rules:
   - If EMAIL LENGTH is short: write 2 short paragraphs.
   - If EMAIL LENGTH is medium: write 3 to 4 short paragraphs.
   - If EMAIL LENGTH is long: write 4 to 6 paragraphs.

4. Tone rules:
   - professional: clear, polished, organizational.
   - warm: friendly, welcoming, and encouraging.
   - donor: emphasize gratitude, impact, and support.
   - church: emphasize community, partnership, care, and service.

5. whatsapp_message:
   - Maximum 500 characters.
   - Short message telling people the PDF/report/newsletter is attached or available by email.

6. summary:
   - Internal summary only.
   - Maximum 3 sentences.

7. suggested_groups:
   - Choose only from AVAILABLE GROUPS.
   - Never invent group names.

8. email_body_zh:
   - Write a professional Traditional Chinese version of the email.
   - Use Traditional Chinese characters only.
   - Never use Simplified Chinese characters.
   - The Chinese version should sound natural to Cantonese-speaking and Traditional Chinese readers.
   - Do not perform a word-for-word translation.
   - Rewrite the message naturally while preserving the meaning, tone, and intent.
   - Use nonprofit and community-oriented language appropriate for Living Water Counselling Centre.
   - Use complete, grammatically correct Traditional Chinese sentences.
   - Do not output transliterations, mixed languages, corrupted characters, or placeholder text.
   - The Chinese version should be similar in length to the English version.

IMPORTANT:
The email should sound like it is accompanying an attachment, not replacing the attachment.
If generating Chinese text, output fluent Traditional Chinese suitable for Hong Kong and Chinese communities in Canada.
Never output Simplified Chinese.
Never output garbled, corrupted, or nonsensical Chinese text.


PDF CONTENT:
{pdf_text[:6000]}
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
            "num_predict": 2500,
        },
    )

    content = response["message"]["content"]
    print("========== RAW AI RESPONSE ==========")
    print(content)
    print("=====================================")
    return extract_json_from_text(content)