import os

from flask import Flask, make_response, render_template, request

app = Flask(__name__)

FLAG = os.environ.get("FLAG", "FLAG{cookie_trust_issue}")


@app.route("/")
def home():
    role = request.cookies.get("role")
    resp = make_response(render_template("index.html", role=role or "user"))
    if role is None:
        resp.set_cookie("role", "user", path="/")
    return resp


@app.route("/flag")
def flag():
    role = request.cookies.get("role", "user")
    if role == "admin":
        return render_template("flag_ok.html", flag=FLAG)
    return render_template("flag_denied.html"), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
