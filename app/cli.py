
from app.records import load_records, search, count_by, get_by_id


def display_records(records):
    if not records:
        print("\nNo articles found.")
        return

    for article in records:
        print("\n" + "=" * 55)
        print("Article Number:", article["article_no"])
        print("Title:", article["title"])
        print("Part:", article["part"])
        print("Text:", article["text"])


def main():
    records = load_records()

    while True:
        print("\n========== SAMVIDHANSATHI ==========")
        print("1. Display all articles")
        print("2. Search articles")
        print("3. Count articles by Part")
        print("4. Find article by number")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            display_records(records)

        elif choice == "2":
            keyword = input("Enter keyword: ").strip()

            if keyword:
                results = search(records, keyword)
                display_records(results)
            else:
                print("Please enter a valid keyword.")

        elif choice == "3":
            counts = count_by(records)

            print("\nArticle count by Part:")

            for part, total in counts.items():
                print(f"{part}: {total}")

        elif choice == "4":
            article_no = input("Enter article number: ").strip()

            result = get_by_id(records, article_no)

            if result:
                display_records([result])
            else:
                print("Article not found.")

        elif choice == "5":
            print("\nThank you for using SamvidhanSathi!")
            break

        else:
            print("\nInvalid choice. Please enter 1 to 5.")


if __name__ == "__main__":
    main()
