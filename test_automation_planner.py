from brain.automation_planner import planner


print()
print("===== DRAX AUTOMATION PLANNER TEST =====")
print()

result = planner.build_plan(
    "Search YouTube for Minecraft tutorials"
)

print(result)

print()
print("===== TEST COMPLETE =====")