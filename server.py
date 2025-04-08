from flask import Flask, render_template, request, jsonify
import os
import json
import subprocess

app = Flask(__name__)

# File to store user credentials
USER_FILE = "users.json"

# Ensure the user file exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as file:
        json.dump([], file)

# Load user data
def load_users():
    with open(USER_FILE, "r") as file:
        return json.load(file)

# Save user data
def save_users(users):
    with open(USER_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Root route to serve signup page
@app.route('/')
def home():
    return render_template('signup.html')

# Serve the signup page
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

# Handle signup submission
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    # Check if the user already exists
    if any(user['username'] == username for user in users):
        return jsonify({"success": False, "message": "User already exists. Please sign in."})

    # Save the new user
    users.append({"username": username, "password": password})
    save_users(users)

    return jsonify({"success": True, "message": "Signup successful! Redirecting to sign-in page."})

# Serve the signin page
@app.route('/signin')
def signin_page():
    return render_template('signin.html')

# Handle signin submission
@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    users = load_users()

    # Check if the credentials match
    if any(user['username'] == username and user['password'] == password for user in users):
        # Run Streamlit app
        subprocess.Popen(["streamlit", "run", "app.py"], shell=True)
        return jsonify({"success": True, "message": "Login successful!"})
    else:
        return jsonify({"success": False, "message": "Email not found, please signup."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)




