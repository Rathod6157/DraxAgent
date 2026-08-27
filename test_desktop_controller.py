from desktop_controller import desktop


print()
print("===== DRAX DESKTOP CONTROL TEST =====")
print()


print("1. Checking mouse position...")

result = desktop.execute({
    "type": "mouse_position"
})

print(result)


print()
print("2. Taking screenshot...")

result = desktop.execute({
    "type": "screenshot",
    "path": "memory/drax_test.png"
})

print(result)


print()
print("3. Opening YouTube...")

result = desktop.execute({
    "type": "open_url",
    "url": "https://www.youtube.com"
})

print(result)


print()
print("===== TEST COMPLETE =====")