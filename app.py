from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
def init_db():
    conn = sqlite3.connect('bank_app.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        bank_account TEXT,
                        employment_status TEXT,
                        income REAL,
                        default_record TEXT,
                        loan_amount REAL,
                        loan_period INTEGER,
                        loan_usage TEXT,
                        credit_score INTEGER,
                        approval TEXT
                    )''')
    conn.commit()
    conn.close()

init_db()

# Helper function: Calculate credit score
def calculate_credit_score(employment_status, income, default_record):
    score = 0
    # Example logic: adjust weight based on employment and income
    if employment_status.lower() in ['employed', 'full-time']:
        score += 40
    else:
        score += 20
    score += min(int(income/1000), 40)  # Normalize income contribution up to 40 points

    if default_record.lower() == 'yes':
        score -= 30  # penalty for default record
    else:
        score += 10

    # Ensure score is between 0 and 100
    score = max(0, min(100, score))
    return score

# Helper function: Loan approval logic
def loan_approval(credit_score, loan_amount):
    # A very basic logic: if credit score exceeds a threshold based on loan amount, approve
    threshold = 50 + loan_amount/1000  # simple formula: higher loan amounts require a higher score
    return "Approved" if credit_score >= threshold else "Rejected"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/business_department', methods=['GET', 'POST'])
def business_department():
    if request.method == 'POST':
        # Collect form data
        name = request.form['name']
        bank_account = request.form['bank_account']
        employment_status = request.form['employment_status']
        income = float(request.form['income'])
        default_record = request.form['default_record']
        loan_amount = float(request.form['loan_amount'])
        loan_period = int(request.form['loan_period'])
        loan_usage = request.form['loan_usage']

        # Calculate credit score
        credit_score = calculate_credit_score(employment_status, income, default_record)
        approval = loan_approval(credit_score, loan_amount)

        # Save data into the database
        conn = sqlite3.connect('bank_app.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO applications 
                          (name, bank_account, employment_status, income, default_record, loan_amount, loan_period, loan_usage, credit_score, approval)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (name, bank_account, employment_status, income, default_record, loan_amount, loan_period, loan_usage, credit_score, approval))
        conn.commit()
        conn.close()

        flash("Application submitted successfully!")
        return redirect(url_for('result', application_id=cursor.lastrowid))
    return render_template('business_department.html')

@app.route('/result/<int:application_id>')
def result(application_id):
    conn = sqlite3.connect('bank_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, credit_score, approval FROM applications WHERE id=?", (application_id,))
    app_data = cursor.fetchone()
    conn.close()
    if app_data:
        return render_template('result.html', name=app_data[0], credit_score=app_data[1], approval=app_data[2])
    else:
        flash("Application not found.")
        return redirect(url_for('index'))

@app.route('/risk_management')
def risk_management():
    # For demonstration: List all applications with credit scores
    conn = sqlite3.connect('bank_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, credit_score, approval FROM applications")
    applications = cursor.fetchall()
    conn.close()
    return render_template('risk_management.html', applications=applications)

if __name__ == '__main__':
    app.run(debug=True)
