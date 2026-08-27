from brain.visual_automation import visual


print("===== DRAX VISION CLICK TEST =====")

print("\n1. Observing desktop...")

observation = visual.observe(
    instruction=(
        "Find visible interactive UI elements. "
        "Look especially for the Visual Studio Code "
        "Terminal tab."
    )
)

print("Observation:")
print(observation)


if not observation.get("success"):
    print("\nVision failed.")
    raise SystemExit(1)


print("\n2. Looking for Terminal...")

element = visual.find_element(
    observation["vision"],
    "Terminal"
)

print("Detected element:")
print(element)


if not element:
    print("\nTerminal was not detected.")
    raise SystemExit(1)


print("\n3. Clicking Terminal using vision...")

result = visual.click_element(element)

print("Click result:")
print(result)


if result.get("success"):
    print("\n🔥 DRAX SUCCESSFULLY CLICKED USING VISION 🔥")
else:
    print("\nClick failed.")


print("\n===== TEST COMPLETE =====")