
from data.sample_records import RECORDS


# 1. Load all article records
def load_records():
    return RECORDS


# 2. Search articles using a keyword
def search(records, keyword):
    results = []

    keyword = keyword.lower()

    for article in records:
        if (keyword in article["text"].lower()
            or keyword in article["title"].lower()
            or keyword in article["article_no"].lower()
            or keyword in article["category"].lower()):

            results.append(article)

    return results


# 3. Count articles category-wise
def count_by(records):
    category_count = {}

    for article in records:
        category = article["category"]

        if category in category_count:
            category_count[category] += 1
        else:
            category_count[category] = 1

    return category_count


# 4. Get an article using its article number
def get_by_id(records, article_no):
    for article in records:
        if article["article_no"].lower() == article_no.lower():
            return article

    return None
