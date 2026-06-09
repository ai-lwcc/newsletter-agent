import json
import os
import re

import ollama

from core.document_text_service import extract_text_from_campaign_file
from core.models import Group


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
        raise ValueError(
            f"AI did not return JSON. Response was: {text[:500]}"
        )

    return json.loads(match.group(0))


def get_email_length_rules(email_length):
    if email_length == "medium":
        return (
            "Write a medium-length email. "
            "Use 3 to 5 short paragraphs. "
            "Include 2 to 4 key highlights from the attached file(s)."
        )

    if email_length == "long":
        return (
            "Write a longer newsletter-style email. "
            "Use 5 to 7 short paragraphs. "
            "Include several key highlights, but still do not replace the attached file(s)."
        )

    return (
        "Write a short accompanying email. "
        "Use 2 to 4 short paragraphs only. "
        "Include only 1 to 3 key highlights from the attached file(s)."
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


def get_file_description(campaign):
    if not campaign.primary_attachment:
        return "attached file"

    filename = campaign.primary_attachment.name.lower()

    if filename.endswith(".pdf"):
        return "attached PDF"

    if filename.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return "attached image, flyer, or poster"

    return "attached file"


def generate_campaign_ai_draft(campaign):
    if not campaign.primary_attachment:
        raise ValueError(
            "Campaign must have an attachment before generating AI draft."
        )

    document_text_parts = []

    attachments = campaign.attachments.all()

    if attachments.exists():
        for attachment in attachments:
            text = extract_text_from_campaign_file(
                attachment.file.path
            )

            document_text_parts.append(
                f"FILE: {attachment.file.name}\n{text}"
            )
    else:
        text = extract_text_from_campaign_file(
            campaign.primary_attachment.path
        )

        document_text_parts.append(
            f"FILE: {campaign.primary_attachment.name}\n{text}"
        )

    document_text = "\n\n---\n\n".join(document_text_parts)

    print("\n========== DOCUMENT LENGTH ==========")
    print(len(document_text))
    print("=====================================\n")

    print("\n========== DOCUMENT PREVIEW ==========")
    print(document_text[:1000])
    print("======================================\n")

    available_groups = list(
        Group.objects.values_list("name", flat=True)
    )

    email_length = getattr(campaign, "email_length", "short")
    tone = getattr(campaign, "tone", "professional")
    file_description = get_file_description(campaign)

    email_length_rules = get_email_length_rules(email_length)
    tone_rules = get_tone_rules(tone)

    prompt = f"""
You are an experienced nonprofit communications assistant.

Your job is NOT to summarize the entire attached file or files in detail.

Your job is to write an email message that will be sent together with the attached file or files.

The attached file(s) will be included in the email, so the email body should introduce the attachment(s) and encourage the reader to open them.

The attached file(s) may be:
- a PDF report
- a poster
- a flyer
- a PNG image
- a JPG/JPEG image
- a WEBP image
- an event announcement
- a community update
- a program brochure

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
   - Match the attached file's purpose, such as annual report, event poster, flyer, program update, or announcement.

2. email_body:
   - This email is only an accompanying message for the attached file(s).
   - Do not restate the whole attached file(s).
   - Mention that the full file(s) is attached.
   - Include only 1 to 3 key highlights from the attached file(s).
   - If the file is an event poster or flyer, include the event name, date, time, location, and call to action when available.
   - If the file is a report, include a short overview and invite readers to review the attachment.
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
   - Short message telling people the attached file/report/newsletter/poster/flyer is available by email.
   - If it is an event, include the most important event detail if available.

6. summary:
   - Internal summary only.
   - Maximum 3 sentences.
   - Describe what the attached file(s) is about.

7. suggested_groups:
   - Choose only from AVAILABLE GROUPS.
   - Never invent group names.
   - Choose groups based on the attached file's audience and purpose.

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

ATTACHED FILE CONTENT:
{document_text[:6000]}
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
                    "Do not return explanation text. "
                    "All JSON string fields must contain useful content."
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