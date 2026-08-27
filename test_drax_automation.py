from brain.desktop_automation import run_automation


print()
print("===== DRAX NATURAL AUTOMATION TEST =====")
print()

instruction = "Search YouTube for Minecraft tutorials"

print(f"Instruction: {instruction}")
print()

result = run_automation(
    instruction
)

print(result)

print()
print("===== TEST COMPLETE =====")