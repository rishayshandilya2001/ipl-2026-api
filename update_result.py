import json

with open("matches.json") as f:
    matches = json.load(f)

played = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]

for m in matches:
    if m["match_no"] in played:
        m["result"] = "Still to be updated"
    else:
        m["result"] = "Still to be played"

with open("matches.json", "w") as f:
    json.dump(matches, f, indent=2)

print("Done! Results field added to all matches.")