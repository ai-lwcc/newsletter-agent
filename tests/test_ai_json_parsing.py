from core.ai_service import extract_json_from_text


def test_extract_json_from_clean_json():
    text = '{"email_subject": "Test", "suggested_groups": ["General Newsletter"]}'

    result = extract_json_from_text(text)

    assert result["email_subject"] == "Test"


def test_extract_json_from_markdown_json():
    text = """
```json
{
  "email_subject": "Test",
  "suggested_groups": ["General Newsletter"]
}
"""
    result = extract_json_from_text(text)
    assert result["email_subject"] == "Test"

def test_extraction_json_from_explanation_test():
    text="""
Here is the JSON:
{
"email_subject":"Test",
"suggested_groups":["General Newsletter"]
}
"""
    result = extract_json_from_text(text)
    assert result["suggested_groups"] == ["General Newsletter"]
