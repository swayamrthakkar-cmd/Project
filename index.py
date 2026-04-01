import tkinter as tk
import re
import requests
import smtplib
import hashlib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Firebase URL
url = "https://json-upload-66dac-default-rtdb.firebaseio.com/"

root = tk.Tk()
root.geometry('2000x700')
root.title('Dynamicity')


# ---------------- DASHBOARD ----------------
def open_dashboard(user_data):
    for widget in root.winfo_children():
        widget.destroy()

    dashboard_frame = tk.Frame(root)
    dashboard_frame.pack(fill='both', expand=True)

    def logout():
        for widget in root.winfo_children():
            widget.destroy()
        show_home()

    tk.Button(dashboard_frame, text="Logout", command=logout).pack(anchor='ne', padx=20, pady=10)

    tk.Label(dashboard_frame, text=f"{user_data['username']}'s Watchlist", font=("Arial", 20)).pack(pady=20)

    watchlist_box = tk.Listbox(dashboard_frame, width=50, height=15)
    watchlist_box.pack(pady=10)

    if "watchlist" in user_data:
        for word in user_data["watchlist"]:
            watchlist_box.insert(tk.END, word)

    word_entry = tk.Entry(dashboard_frame)
    word_entry.pack(pady=5)

    def add_word():
        word = word_entry.get()
        if word:
            watchlist_box.insert(tk.END, word)
            word_entry.delete(0, tk.END)
            update_watchlist(user_data["username"], word)

    tk.Button(dashboard_frame, text="Add Word", command=add_word).pack(pady=10)


# ---------------- UPDATE WATCHLIST ----------------
def update_watchlist(username, new_word):
    firebase_url = url + "users.json"
    data = requests.get(firebase_url).json() or {}

    for key, user in data.items():
        if user.get("username") == username:
            if "watchlist" not in user:
                user["watchlist"] = []
            user["watchlist"].append(new_word)

            requests.put(url + f"users/{key}.json", json=user)
            return


# ---------------- REGISTER ----------------
def register_command():
    for widget in root.winfo_children():
        widget.destroy()

    register_frame = tk.Frame(root)
    register_frame.pack(fill='both', expand=True)

    tk.Label(register_frame, text='Username: ').place(x=50, y=50)
    username_entry = tk.Entry(register_frame)
    username_entry.place(x=120, y=50)

    tk.Label(register_frame, text='Password: ').place(x=50, y=80)
    password_entry = tk.Entry(register_frame, show="*")
    password_entry.place(x=120, y=80)

    tk.Label(register_frame, text='First Name: ').place(x=50, y=110)
    firstname_entry = tk.Entry(register_frame)
    firstname_entry.place(x=120, y=110)

    tk.Label(register_frame, text='Last Name: ').place(x=50, y=140)
    lastname_entry = tk.Entry(register_frame)
    lastname_entry.place(x=120, y=140)

    tk.Label(register_frame, text='Email: ').place(x=50, y=170)
    email_entry = tk.Entry(register_frame)
    email_entry.place(x=120, y=170)

    error_label = tk.Label(register_frame, text="", fg="red")
    error_label.place(x=50, y=230)

    def is_valid_email(email):
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

    def signin_command():
        username = username_entry.get()
        password = password_entry.get()
        first_name = firstname_entry.get()
        last_name = lastname_entry.get()
        email = email_entry.get()

        if not is_valid_email(email):
            error_label.config(text='Invalid email format')
            return

        firebase_url = url + "users.json"
        data = requests.get(firebase_url).json() or {}

        for user in data.values():
            if user.get("username") == username:
                error_label.config(text="Username already taken!")
                return
            if user.get("email") == email:
                error_label.config(text="Email already in use!")
                return

        # SEND EMAIL
        try:
            sender_email = "xxxxxxxxxxxxxxxx"
            app_password = "xxxx xxxx xxxx xxxx"  # NO SPACES

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = email
            msg["Subject"] = "Registration Confirmation"

            body = f"Hi {first_name},\nThis is a confirmation email for your registration on Lumos Dynamicity. If this was you, ignore this email, sit back, relax and enjoy the rest of your day, but if this was not you, please contact us immediately at 'swayam.r.thakkar@gmail.com',\n\nThanks,\nLumos Support Team"
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)

        except Exception as e:
            print("EMAIL ERROR:", e)
            error_label.config(text="Email failed")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user_data = {
            "username": username,
            "password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "watchlist": []
        }

        requests.post(firebase_url, json=user_data)

        error_label.config(text="Account created!", fg="green")
        open_dashboard(user_data)

    tk.Button(register_frame, text='Sign Up', command=signin_command).place(x=200, y=200)


# ---------------- LOGIN ----------------
def login_command():
    for widget in root.winfo_children():
        widget.destroy()

    login_frame = tk.Frame(root)
    login_frame.pack(fill='both', expand=True)

    tk.Label(login_frame, text='Username:').place(x=50, y=50)
    username_entry = tk.Entry(login_frame)
    username_entry.place(x=120, y=50)

    tk.Label(login_frame, text='Password:').place(x=50, y=80)
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.place(x=120, y=80)

    error_label = tk.Label(login_frame, text="", fg="red")
    error_label.place(x=50, y=150)

    def check_login():
        username = username_entry.get()
        password = password_entry.get()

        firebase_url = url + "users.json"
        data = requests.get(firebase_url).json() or {}

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        for user in data.values():
            if user.get("username") == username and user.get("password") == hashed_password:
                open_dashboard(user)
                return

        error_label.config(text="Invalid username or password")

    tk.Button(login_frame, text="Login", command=check_login).place(x=120, y=120)


# ---------------- HOME ----------------
def show_home():
    tk.Button(root, text='Register', width=13, command=register_command).place(x=1080, y=30)
    tk.Button(root, text='Login', width=13, command=login_command).place(x=1200, y=30)


# Start
show_home()
root.mainloop()
