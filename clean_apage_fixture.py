import json

# Load the fixture
with open("apage.json", "r") as f:
    data = json.load(f)

# Clean foreign keys that may cause integrity errors
for obj in data:
    model = obj.get("model", "")
    pk = obj.get("pk")
    fields = obj.get("fields", {})

    if "zone" in fields:
        print(f"Removing zone from {model} pk={pk}")
        del fields["zone"]

    if "site" in fields:
        print(f"Removing site from {model} pk={pk}")
        del fields["site"]

    if "state" in fields:
        print(f"Removing state from {model} pk={pk}")
        del fields["state"]

    if "created_by" in fields:
        print(f"Removing created_by from {model} pk={pk}")
        del fields["created_by"]

    # Optional: if you know any more fields causing trouble, add here
    # if "client" in fields:
    #     del fields["client"]

# Save cleaned fixture
with open("apage_cleaned.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Cleaned fixture saved as apage_cleaned.json")