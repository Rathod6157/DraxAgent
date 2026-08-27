from brain.desktop_automation import automation


print()
print("===== DRAX AUTOMATION TEST =====")
print()


plan = [

    {
        "type": "open_url",
        "url": "https://www.youtube.com"
    },

    {
        "type": "wait",
        "seconds": 2
    },

    {
        "type": "hotkey",
        "keys": ["ctrl", "l"]
    },

    {
        "type": "type",
        "text": "Minecraft"
    },

    {
        "type": "press",
        "key": "enter"
    },

    {
        "type": "wait",
        "seconds": 3
    },

]


result = automation.execute_plan(
    plan,
    observe=True
)


print(result)

print()
print("===== TEST COMPLETE =====")