from brain.visual_agent import visual_agent


print("===== DRAX VISUAL AGENT TEST =====")

result = visual_agent.run(
    "Click the Terminal tab in Visual Studio Code.",
    target="Terminal",
)

print()
print("FINAL RESULT:")
print(result)

print()
print("===== TEST COMPLETE =====")