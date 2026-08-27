from brain.screen_vision import vision


print("===== DRAX AI VISION TEST =====")

image = "memory/perception_test.png"

print("\nAnalyzing screenshot...")
print("This may take a few seconds...\n")

result = vision.analyze(
    image,
    instruction=(
        "Describe what Drax can currently see on the desktop. "
        "Pay special attention to clickable buttons, text fields, "
        "links, and their approximate locations."
    ),
)

print(result)

print("\n===== TEST COMPLETE =====")