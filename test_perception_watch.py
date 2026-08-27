from brain.perception import perception


print()
print("===== DRAX PERCEPTION WATCH TEST =====")
print()

print("Watching desktop for 3 seconds...")
print()

result = perception.watch(
    duration=3,
    interval=0.5,
)

print("Observation count:", len(result["observations"]))

for index, observation in enumerate(
    result["observations"],
    start=1
):

    print()
    print(f"Observation #{index}")

    print(
        "Screen:",
        observation["screen"]
    )

    print(
        "Mouse:",
        observation["mouse"]
    )

    print(
        "Screenshot:",
        observation["screenshot"]
    )

print()
print("===== TEST COMPLETE =====")