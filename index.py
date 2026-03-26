import json
import os

import tKinter as tk

FILE_NAME = "accounts.json"

# Load data from file
def load_data():
    if not os.path.exists(FILE_NAME):
        return {}
    with open(FILE_NAME, "r") as f:
        return json.load(f)

# Save data to file
def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f)

# Register user
def register(data):
    username = input("Enter username: ")
    if username in data:
        print("Username already exists!")
        return
    
    password = input("Enter password: ")
    data[username] = {
        "password": password,
        "watchlist": []
    }
    save_data(data)
    print("Account created!")

# Login user
def login(data):
    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in data and data[username]["password"] == password:
        print("Login successful!")
        user_menu(data, username)
    else:
        print("Invalid credentials!")

# User menu after login
def user_menu(data, username):

    while True:
        print("\n1. Add word to watchlist")
        print("2. View watchlist")
        print("3. Logout")

        choice = input("Choose: ")

        if choice == "1":
            word = input("Enter word: ")
            data[username]["watchlist"].append(word)
            save_data(data)
            print("Added!")

        elif choice == "2":
            print("Your watchlist:", data[username]["watchlist"])

        elif choice == "3":
            break

        else:
            print("Invalid choice")

# Main program
def main():
    data = load_data()

    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose: ")

        if choice == "1":
            register(data)
        elif choice == "2":
            login(data)
        elif choice == "3":
            break
        else:
            print("Invalid choice")

main()