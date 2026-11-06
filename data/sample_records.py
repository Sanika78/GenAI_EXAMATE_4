RECORDS = [
    {
        "id": 12,
        "title": "Definition of State",
        "category": "Fundamental Rights",
        "text": "In this Part, unless the context otherwise requires, the State includes..."
    },
    {
        "id": 13,
        "title": "Laws inconsistent with Fundamental Rights",
        "category": "Fundamental Rights",
        "text": "All laws in force immediately before the commencement of this Constitution..."
    }
]
for article in RECORDS:
    print(article)

keyword = input("Enter keyword: ").lower()
for article in RECORDS:
    if keyword in article["text"].lower():
        print(article)

for article in RECORDS:
    print(article["category"])