import os


SYSTEM_INSTRUCTION = """
You are EduGenie, an AI personalized learning tutor.

Give clear, beginner-friendly answers suitable for college students.

Use simple English.

When useful, use:

- headings
- bullet points
- examples
- short step-by-step explanations
- practice questions

Do not invent facts.

If the question is ambiguous,
state the assumption.
"""


# --------------------------------------------------
# DEMO FALLBACK
# --------------------------------------------------

def _fallback(
    prompt,
    mode
):

    topic = prompt.strip()


    if mode == "summary":

        return (
            f"Summary of {topic}:\n\n"

            f"• Start with the definition of {topic}.\n"

            "• Identify its main concepts or steps.\n"

            "• Learn one practical example.\n"

            "• Test yourself with a short question.\n\n"

            "Add a few textbook points for exam preparation."
        )


    if mode == "quiz":

        return (
            f"Practice Quiz — {topic}\n\n"

            "1. What is the basic definition?\n"

            "2. What are two important features?\n"

            "3. Give one real-world example.\n\n"

            "Try answering without looking at your notes."
        )


    if mode == "example":

        return (
            f"Example for {topic}:\n\n"

            f"Imagine a simple college project "
            f"that uses {topic}.\n\n"

            "First identify the input, "
            "then process it, "
            "and finally show the output.\n\n"

            "This connects the concept "
            "to a practical application."
        )


    return (
        f"Let's learn {topic} step by step.\n\n"

        "1. Understand the definition.\n"

        "2. Learn the key parts.\n"

        "3. See a small example.\n"

        "4. Practice it yourself.\n\n"

        "Tip: If you provide the exact chapter, "
        "question, or code, EduGenie can explain "
        "that specific material."
    )


# --------------------------------------------------
# GEMINI AI
# --------------------------------------------------

def generate_ai_response(
    prompt,
    mode="explain"
):

    api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()


    # No API key = demo mode
    if not api_key:

        return (
            _fallback(
                prompt,
                mode
            ),
            "demo"
        )


    try:

        from google import genai


        client = genai.Client(
            api_key=api_key
        )


        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )


        task = {

            "explain":
                "Explain the topic clearly.",

            "summary":
                "Create a concise study summary.",

            "example":
                "Give a simple practical example.",

            "quiz":
                "Create 5 short quiz questions and answers."

        }.get(
            mode,
            "Explain the topic clearly."
        )


        response = client.models.generate_content(

            model=model,

            contents=(
                f"{SYSTEM_INSTRUCTION}\n\n"
                f"Task: {task}\n\n"
                f"Topic/question: {prompt}"
            )
        )


        text = getattr(
            response,
            "text",
            None
        )


        if text:

            return (
                text,
                "gemini"
            )


        return (
            _fallback(
                prompt,
                mode
            ),
            "demo"
        )


    except Exception:

        return (
            _fallback(
                prompt,
                mode
            ),
            "demo"
        )