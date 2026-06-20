from flask import Flask, render_template, request, session
from datetime import timedelta
import tinydb
from tinydb import Query
from google import generativeai as genai  # ✅ תיקון כאן

# הגדרת מפתח API
genai.configure(api_key="AIzaSyAFoYJT1PGhH_0RSKH_fIZAfAJSqfHXVKc")

# יצירת המודל והשיחה
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

# הגדרת בסיס נתונים
database = tinydb.TinyDB("data.json")

# הגדרות Flask
app = Flask(__name__)
app.secret_key = "asaf2706"
app.permanent_session_lifetime = timedelta(days=10)

@app.route('/')
def home():
    if "user" in session:
        return render_template("Hello.html", username=session["user"])
    return render_template("home.html")

@app.route('/logout')
def userlogout():
    session.pop("user", None)
    return render_template("home.html")

@app.route('/login')
def loginPage():
    return render_template("login.html")

@app.route("/api/signup", methods=["POST"])
def userSignup():
    mail = request.form.get("email")
    name = request.form.get("username")
    password = request.form.get("password")

    database.insert({
        "email": mail,
        "username": name,
        "password": password
    })

    session.permanent = True
    session["user"] = name
    return render_template("Hello.html", username=name)

@app.route("/api/login", methods=["POST"])
def userLogin():
    mail = request.form.get("email")
    password = request.form.get("password")

    userQuery = Query()
    user = database.get(userQuery.email == mail)

    if not user:
        return render_template("signup.html", error="לא קיים משתמש עם המייל הזה")
    if user["password"] != password:
        return render_template("login.html", error="סיסמה לא נכונה")

    session.permanent = True
    session["user"] = user["username"]
    return render_template("Hello.html", username=user["username"])

@app.route('/signup')
def signupPage():
    return render_template("signup.html")

@app.route('/bye')
def sayBay():
    return render_template("bye.html")

@app.route('/hi/<name>')
def hi(name):
    return f"Hi {name}!"

# ✅ שיחה מתמשכת עם Gemini
@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question")
    response = chat.send_message(question)
    answer = response.text

    return render_template("Hello.html",
                           username=session.get("user", "משתמש"),
                           answer=answer)

if __name__ == "__main__":
    app.run(debug=True)