from brain.ai import ai

print(
    "Talking to Drax..."
)

reply = ai.reason(
    """
You are Drax.

Introduce yourself in one sentence.

Don't mention Gemini.

Don't mention Google.

Just introduce yourself.
"""
)

print()

print(reply)