from pipeline import ask_database


question = "Show total sales by category"

response = ask_database(question)

print("\nUser Question:")
print(question)

if response["success"]:

    print("\nSQL executed successfully.")

    print("\nQuery Result:")
    print(response["result"].to_string(index=False))

    if response["chart"]:

        print("\nChart created successfully!")

    else:

        print("\nNo suitable chart was created.")

else:

    print("\nQuery failed.")
    print("Error:", response["error"])