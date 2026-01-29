import json

with open("apage_cleaned.json", "r") as f:
    data = json.load(f)

# List of models you want to keep
keep_models = [
    "apage.servicereport",
    "apage.servicereportattachment",
    "apage.electronicitemstatus",
    "apage.electronicpanelstatus",
    "apage.chemicalitemstatus",
    "apage.pumpstatus",
    "apage.miscellaneousitemstatus",
    "apage.wastewaterparameterstatus",
    "apage.machineruntime",
    "apage.toolstatus",
    # Add more related models if needed
]

filtered = [obj for obj in data if obj["model"] in keep_models]

with open("apage_service_only.json", "w") as f:
    json.dump(filtered, f, indent=2)

print(f"✅ Saved {len(filtered)} entries to apage_service_only.json")