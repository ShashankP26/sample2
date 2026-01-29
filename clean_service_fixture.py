import json

with open("apage_service_final.json", "r") as f:
    data = json.load(f)

clean_fields = ["site", "zone", "created_by", "state"]

for obj in data:
    fields = obj.get("fields", {})
    for key in clean_fields:
        if key in fields:
            print(f"Removing {key} from {obj['model']} pk={obj['pk']}")
            del fields[key]

with open("apage_service_cleaned.json", "w") as f:
    json.dump(data, f, indent=2)

print("✅ Cleaned fixture saved as apage_service_cleaned.json")