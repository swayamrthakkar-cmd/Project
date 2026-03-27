import tkinter as tk

import re

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import smtplib

import json
import os

root = tk.Tk()
root.geometry('2000x700')
root.title('Dynamicity')

def open_dashboard(user_data):
    # Clear window
    for widget in root.winfo_children():
        widget.destroy()

    dashboard_frame = tk.Frame(root)
    dashboard_frame.pack(fill='both', expand=True)

    def logout():
        
        for widget in root.winfo_children():
            widget.destroy()

        register = tk.Button(text='Register', width=13, command=register_command)
        register.place(x=1080,y=30)

        login = tk.Button(text='Login', width=13, command=login_command)
        login.place(x=1200, y=30)

    # Top bar
    logout_button = tk.Button(dashboard_frame, text="Logout", command=logout)
    logout_button.pack(anchor='ne', padx=20, pady=10)

    # Title
    title = tk.Label(dashboard_frame, text=f"{user_data['username']}'s Watchlist", font=("Arial", 20))
    title.pack(pady=20)

    # Watchlist display
    watchlist_box = tk.Listbox(dashboard_frame, width=50, height=15)
    watchlist_box.pack(pady=10)

    # Load existing watchlist (if exists)
    if "watchlist" in user_data:
        for word in user_data["watchlist"]:
            watchlist_box.insert(tk.END, word)

    # Entry to add word
    word_entry = tk.Entry(dashboard_frame)
    word_entry.pack(pady=5)

    # Add word function
    def add_word():
        word = word_entry.get()
        if word:
            watchlist_box.insert(tk.END, word)
            word_entry.delete(0, tk.END)

            # Update JSON
            update_watchlist(user_data["username"], word)

    add_btn = tk.Button(dashboard_frame, text="Add Word", command=add_word)
    add_btn.pack(pady=10)

def update_watchlist(username, new_word):
    file_name = "users.json"

    with open(file_name, "r") as file:
        data = json.load(file)

    for user in data:
        if user["username"] == username:
            if "watchlist" not in user:
                user["watchlist"] = []
            user["watchlist"].append(new_word)

    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

def register_command():
    register_frame = tk.Frame()
    register_frame.pack(fill='both', expand=True)

    username_label = tk.Label(text='Username: ')
    username_label.place(x=50, y=50)
    username_entry = tk.Entry()
    username_entry.place(x=120, y=50)

    password_label = tk.Label(text='Password: ')
    password_label.place(x=50, y=80)
    password_entry = tk.Entry()
    password_entry.place(x=120 ,y=80)

    firstname_label = tk.Label(text='First Name: ')
    firstname_label.place(x=50, y=110)
    firstname_entry = tk.Entry()
    firstname_entry.place(x=120 ,y=110)

    lastname_label = tk.Label(text='Last Name: ')
    lastname_label.place(x=50, y=140)
    lastname_entry = tk.Entry()
    lastname_entry.place(x=120 ,y=140)

    email_label = tk.Label(text='email: ')
    email_label.place(x=50, y=170)
    email_entry = tk.Entry()
    email_entry.place(x=120 ,y=170)

    error_label = tk.Label(register_frame, text="", fg="red")
    error_label.place(x=50, y=230)

    def signin_command():

        def is_valid_email(email):
            pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            return re.match(pattern, email)

        sender_email = 'swayam.r.thakkar@gmail.com'
        app_password = 'ovxu lgpj qpnf nuiv'

        error_label = tk.Label(register_frame, text='Email does not exist', fg="red")
        error_label.place(x=50, y=250)

        username = username_entry.get()
        password = password_entry.get()
        first_name = firstname_entry.get()
        last_name = lastname_entry.get()
        email = email_entry.get()
        
        if not is_valid_email(email):
            error_label = tk.Label(register_frame, text='Invalid email format', fg="red")
            error_label.place(x=50, y=220)
            return

        reciever_email = email

        msg = MIMEMultipart()
    
        msg["From"] = sender_email
        msg["To"] = reciever_email
        msg["Subject"] = 'Registeration Cofirmation'

        body = f'Hi {first_name}, \nThis is a confirmation email from LUMOS, if you have registered on the Lumos system, sit back, relax and enjoy the rest of your day, but if it weren\'t you please contact us ASAP at "swayam.r.thakkar@gmail.com".\n\nThanks,\nLumos Support Team'
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure connection
        server.login(sender_email, app_password)

        # Send email
        try:
            server.send_message(msg)
        except smtplib.SMTPRecipientsRefused:
            error_label = tk.Label(register_frame, text='Email does not exist', fg="red")
            error_label.place(x=50, y=240)
            return
        except Exception:
            error_label = tk.Label(register_frame, text='Failed to send email', fg="red")
            error_label.place(x=50, y=240)
            return
            

        # Close connection
        server.quit()

        file_name = "users.json"

        # Load existing users
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                try:
                    data = json.load(file)
                except:
                    data = []
        else:
            data = []

        for user in data:
            if user["username"] == username:
                error_label.config(text="Username already taken!")
                return
            if user["email"] == email:
                error_label.config(text="Email already in use!")
                return

        user_data = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "watchlist": []
        }

        data.append(user_data)

        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)

        error_label.config(text="Account created!", fg="green")

        # Go to dashboard
        open_dashboard(user_data)
        
    signin = tk.Button(text='sign in', command=signin_command)
    signin.place(x=200, y=200)


def login_command():
    # Clear screen
    for widget in root.winfo_children():
        widget.destroy()

    login_frame = tk.Frame(root)
    login_frame.pack(fill='both', expand=True)

    username_label = tk.Label(login_frame, text='Username:')
    username_label.place(x=50, y=50)
    username_entry = tk.Entry(login_frame)
    username_entry.place(x=120, y=50)

    password_label = tk.Label(login_frame, text='Password:')
    password_label.place(x=50, y=80)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.place(x=120, y=80)

    def check_login():
        username = username_entry.get()
        password = password_entry.get()

        file_name = "users.json"

        if not os.path.exists(file_name):
            print("No user found")
            return

        with open(file_name, "r") as file:
            data = json.load(file)

        for user in data:
            if user["username"] == username and user["password"] == password:
                print("Login successful!")
                open_dashboard(user)
                return

        error_label = tk.Label(login_frame, text="", fg="red")
        error_label.place(x=50, y=150)
        error_label.config(text='Invalid username or password')

        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

    login_btn = tk.Button(login_frame, text="Login", command=check_login)
    login_btn.place(x=120, y=120)



register = tk.Button(text='Register', width=13, command=register_command)
register.place(x=1080,y=30)

login = tk.Button(text='Login', width=13, command=login_command)
login.place(x=1200, y=30)

root.mainloop()