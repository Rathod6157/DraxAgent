from brain.visual_bridge import visual_bridge


print("===== DRAX VISUAL BRIDGE TEST =====")
print()

instruction = (
    "Find the Problems tab in Visual Studio Code and click it."
)

print("👁️ DRAX VISUAL BRIDGE")
print("Instruction:", instruction)
print()

result = visual_bridge.run(
    instruction,
    target="Problems",
)

print()
print("FINAL RESULT:")
print(result)

print()
print("===== TEST COMPLETE =====")