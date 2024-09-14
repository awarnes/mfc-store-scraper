import json, csv

with open('./hummingbird-91424.json') as file:
    data = json.load(file)

    print(f"Length: {len(data)}")
