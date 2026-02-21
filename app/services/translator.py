from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

TRANSLATOR_MODEL = "google/mt5-small"


tokenizer = AutoTokenizer.from_pretrained(TRANSLATOR_MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(TRANSLATOR_MODEL)


def translate_text(text: str, target_language: str) -> str:
    """
    Translates text from English to the target language using the specified model.

    Args:
        text: The text to translate.
        target_language: The target language to translate to.

    Returns:
        The translated text.
    """
    input_text = (
        f"Translate the following text from English to {target_language}: {text}"
    )

    input_ids = tokenizer(input_text, return_tensors="pt").input_ids
    outputs = model.generate(input_ids)

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
