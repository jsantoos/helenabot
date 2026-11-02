"""
Module: helena_bot.context.prompt_builder

Constructs a context-aware prompt from historical interactions and the current user input.

This module ensures that the prompt:
- Preserves recent interactions in natural dialogue format
- Automatically summarizes history if it exceeds the token budget
- Enforces input sanitization for robustness

Used primarily by the Telegram message/voice handlers before invoking the LLM.

Applies:
- PEP 8: Code style
- PEP 20: Zen of Python
- PEP 257: Docstring conventions
- PEP 484: Type hints
"""

from typing import List

from helena_bot.utils.summarization import summarize_text
from helena_bot.utils.text_cleaning import sanitize_prompt, sanitize_text
from helena_bot.utils.tokening.counter import count_tokens

MAX_TOTAL_TOKENS = 3072


def build_context_safe(past_interactions: List[dict], new_question: str) -> str:
    """
    Build a safe, summarized context prompt based on recent conversation history and a new user input.

    This function:
    - Formats previous Q&A pairs into prompt lines
    - Adds the new question to the context
    - Applies summarization if the total token count exceeds allowed limits

    Args:
        past_interactions (List[dict]): History of {"question": str, "answer": str} pairs.
        new_question (str): The user's new question or message.

    Returns:
        str: A prompt string suitable for LLM input.
    """
    context_lines = []
    new_question = sanitize_text(new_question)

    for interaction in past_interactions:
        q = sanitize_text(interaction.get("question"))
        a = sanitize_text(interaction.get("answer"))
        if q and a:
            context_lines.append(f"Usuário: {q}\nBot: {a}")

    context_lines.append(f"Usuário: {new_question}")
    full_prompt = sanitize_prompt("\n".join(context_lines))

    if count_tokens(full_prompt) <= MAX_TOTAL_TOKENS:
        return full_prompt

    summarized_context = []
    for interaction in past_interactions:
        combined = f"Usuário: {interaction.get('question', '')}\nBot: {interaction.get('answer', '')}"
        summary = summarize_text(combined)
        summarized_context.append(summary)

    summarized_prompt = "\n".join(summarized_context)
    summarized_prompt += f"\nUsuário: {new_question}"
    final_prompt = sanitize_prompt(summarized_prompt.strip())

    if count_tokens(final_prompt) > MAX_TOTAL_TOKENS:
        return summarize_text(final_prompt)

    return final_prompt or f"Usuário: {new_question}"
