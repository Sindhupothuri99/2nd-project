from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "change-this-to-a-long-random-secret"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return {"status": "ok"}

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):

    if role not in ['admin', 'faculty', 'student']:
        return "Invalid role", 404

    error = None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Authentication will be connected to the database next.
        error = "Invalid email or password. Database authentication is not configured yet."

    return render_template(
        'login.html',
        role=role.capitalize(),
        error=error
    )

@app.route('/admin')
def admin():
    return "<h1>Admin Dashboard</h1>"

@app.route('/faculty')
def faculty():
    return "<h1>Faculty Dashboard</h1>"

@app.route('/student')
def student():
    return "<h1>Student Dashboard</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
