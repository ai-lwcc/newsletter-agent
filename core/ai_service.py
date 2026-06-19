import json
import logging
import os
import re

import ollama

from core.document_text_service import extract_text_from_campaign_file
from core.models import Group

logger = logging.getLogger(__name__)

AI_MODEL = os.getenv(
    "AI_MODEL",
    "llama3.1:8b-instruct-q4_K_M",
)


def extract_json_from_text(text):
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


def contains_chinese_characters(text):
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def validate_ai_result(ai_result):
    required_fields = [
        "email_subject",
        "email_body",
        "email_body_zh",
        "whatsapp_message",
        "suggested_groups",
        "summary",
    ]

    for field in required_fields:
        if field not in ai_result:
            raise ValueError(f"AI result missing required field: {field}")

    if contains_chinese_characters(ai_result.get("email_body", "")):
        raise ValueError(
            "AI generated Chinese text inside email_body. "
            "email_body must be English only."
        )

    if not contains_chinese_characters(ai_result.get("email_body_zh", "")):
        raise ValueError(
            "AI did not generate Traditional Chinese text in email_body_zh."
        )

    if not isinstance(ai_result.get("suggested_groups"), list):
        ai_result["suggested_groups"] = []

    return ai_result


def get_email_length_rules(email_length):
    if email_length == "medium":
        return (
            "Write a medium-length email. "
            "Use 3 to 4 short paragraphs for the English body. "
            "Include 2 to 4 key highlights from the uploaded file."
        )

    if email_length == "long":
        return (
            "Write a longer newsletter-style email. "
            "Use 4 to 6 short paragraphs for the English body. "
            "Include several key highlights, but do not replace the attachment."
        )

    return (
        "Write a short accompanying email. "
        "Use 2 short paragraphs for the English body. "
        "Include only 1 to 3 key highlights from the uploaded file."
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


def get_campaign_document_text(campaign):
    text_parts = []

    attachments = campaign.attachments.all()

    if attachments.exists():
        for attachment in attachments:
            extracted_text = extract_text_from_campaign_file(
                attachment.file.path,
            )

            text_parts.append(
                f"FILE: {attachment.file.name}\n{extracted_text}"
            )

    elif campaign.primary_attachment:
        extracted_text = extract_text_from_campaign_file(
            campaign.primary_attachment.path,
        )

        text_parts.append(
            f"FILE: {campaign.primary_attachment.name}\n{extracted_text}"
        )

    else:
        raise ValueError(
            "Campaign must have at least one attachment before generating AI draft."
        )

    document_text = "\n\n---\n\n".join(text_parts).strip()

    if not document_text:
        raise ValueError(
            "No readable text could be extracted from the campaign attachment."
        )

    return document_text


def generate_campaign_ai_draft(campaign):
    document_text = get_campaign_document_text(campaign)

    logger.info(
        "Generating AI draft for campaign_id=%s document_length=%s model=%s",
        campaign.id,
        len(document_text),
        AI_MODEL,
    )

    available_groups = list(
        Group.objects.values_list("name", flat=True)
    )

    email_length = getattr(campaign, "email_length", "short")
    tone = getattr(campaign, "tone", "professional")

    email_length_rules = get_email_length_rules(email_length)
    tone_rules = get_tone_rules(tone)

    prompt = f"""
You are an experienced nonprofit communications assistant.

Your job is to write an accompanying campaign email for the uploaded file.

The uploaded file will be attached to the email, so the email should introduce the attachment and encourage the reader to open it.

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
   - Match the campaign content.
   - Do not include "Dear Supporters" in the subject.

2. email_body:
   - MUST be written in English only.
   - Do not use Chinese characters in email_body.
   - Start exactly with: Dear Supporters,
   - This is the English email body.
   - This email is only an accompanying message for the attached file.
   - Do not restate the whole file.
   - Mention that the full file/report is attached.
   - Include only 1 to 3 key highlights from the uploaded file.
   - Do not include the Chinese translation inside email_body.
   - Do not end with the organization name.

3. email_body_zh:
   - MUST be written in Traditional Chinese only.
   - This is the Traditional Chinese translation/version of email_body.
   - Use Traditional Chinese, not Simplified Chinese.
   - Make it natural for a Hong Kong / Cantonese-speaking nonprofit audience.
   - Keep the same meaning and tone as the English email body.
   - Do not copy the English text.
   - Do not use corrupted, garbled, or nonsensical Chinese.
   - Do not end with the organization name.

4. Final email format:
   The final displayed email should follow this structure:

   Email Subject

   Dear Supporters,

   English Email Body

   Chinese Email Body

   Living Waters Counselling Centre

   Therefore:
   - email_subject should contain only the subject.
   - email_body should contain the English section only.
   - email_body_zh should contain the Chinese section only.
   - The final signature should be handled by the email template or preview template.

5. whatsapp_message:
   - Maximum 500 characters.
   - Short message telling people the file/report/newsletter is attached or available by email.
   - Write in English unless the uploaded file clearly requires Chinese.
   - Do not include excessive detail.

6. summary:
   - Internal summary only.
   - Maximum 3 sentences.

7. suggested_groups:
   - Choose only from AVAILABLE GROUPS.
   - Never invent group names.

IMPORTANT:
The English body and Chinese body must be separate.
email_body must be English only.
email_body_zh must be Traditional Chinese only.
Never put Chinese inside email_body.
Never put English paragraphs inside email_body_zh except unavoidable names like Living Waters Counselling Centre.
Never output Simplified Chinese.
Never output garbled, corrupted, or nonsensical Chinese.

UPLOADED FILE CONTENT:
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
                    "email_body must be English only. "
                    "email_body_zh must be Traditional Chinese only. "
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

    logger.info(
        "Raw AI response received for campaign_id=%s response_length=%s",
        campaign.id,
        len(content),
    )

    ai_result = extract_json_from_text(content)
    ai_result = validate_ai_result(ai_result)

    return ai_result