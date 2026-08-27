from brain.perception import perception


print("===== DRAX PERCEPTION TEST =====")

print("\n1. Screen size...")
print(perception.screen_size())

print("\n2. Mouse position...")
print(perception.mouse_position())

print("\n3. Capturing observation...")
result = perception.observe("perception_test.png")
print(result)

print("\n===== TEST COMPLETE =====")