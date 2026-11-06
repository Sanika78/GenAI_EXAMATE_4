while True:

    print("\n--- SamvidhanSathi Menu ---")
    print("1. About SamvidhanSathi")
    print("2. Sample Questions")
    print("3. Constitution Rule Check")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("SamvidhanSathi helps people learn the Indian Constitution.")

    elif choice == "2":
        print("1. What is the Preamble?")
        print("2. What are Fundamental Rights?")
        print("3. What are Fundamental Duties?")

    elif choice == "3":
        topic = input("Enter 1 for Rights, 2 for Duties, 3 for DPSP: ")

        if topic == "1":
            print("Fundamental Rights: Part III, Articles 12-35.")

        elif topic == "2":
            print("Fundamental Duties: Article 51A.")

        elif topic == "3":
            print("Directive Principles: Part IV, Articles 36-51.")

        else:
            print("Invalid topic.")

    elif choice == "0":
        print("Thank you for using SamvidhanSathi!")
        break

    else:
        print("Invalid choice. Try again.")