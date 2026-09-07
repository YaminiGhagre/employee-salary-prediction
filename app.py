from flask import Flask, render_template, request
import joblib
import mysql.connector
import pandas as pd

app = Flask(__name__)

# ==========================================================
# LOAD ML MODEL
# ==========================================================

model = joblib.load("model/salary_model.pkl")


# ==========================================================
# MYSQL CONNECTION
# ==========================================================

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@789",
        database="employee_salary_db"
    )


# ==========================================================
# HOME PAGE
# ==========================================================

@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    employee = None
    error = None

    if request.method == "POST":

        conn = None
        cursor = None

        try:

            # ------------------------------------------------
            # GET FORM DATA
            # ------------------------------------------------

            name = request.form["name"].strip()

            age = int(request.form["age"])

            gender = request.form["gender"]

            education = request.form["education"]

            experience_years = int(
                request.form["experience_years"]
            )

            job_title = request.form["job_title"]

            department = request.form["department"]

            location = request.form["location"]

            employment_type = request.form["employment_type"]

            performance_rating = float(
                request.form["performance_rating"]
            )

            projects_completed = int(
                request.form["projects_completed"]
            )

            overtime_hours = int(
                request.form["overtime_hours"]
            )

            skills_count = int(
                request.form["skills_count"]
            )


            # ------------------------------------------------
            # VALIDATION
            # ------------------------------------------------

            if age < 18 or age > 65:
                raise ValueError(
                    "Age must be between 18 and 65."
                )

            if experience_years < 0 or experience_years > 50:
                raise ValueError(
                    "Experience must be between 0 and 50 years."
                )

            if performance_rating < 2 or performance_rating > 5:
                raise ValueError(
                    "Performance rating must be between 2 and 5."
                )

            if projects_completed < 0:
                raise ValueError(
                    "Projects completed cannot be negative."
                )

            if overtime_hours < 0:
                raise ValueError(
                    "Overtime hours cannot be negative."
                )

            if skills_count < 1:
                raise ValueError(
                    "Skills count must be at least 1."
                )


            # ------------------------------------------------
            # CREATE DATAFRAME FOR MODEL
            # ------------------------------------------------

            input_data = pd.DataFrame([{

                "age": age,

                "gender": gender,

                "education": education,

                "experience_years": experience_years,

                "job_title": job_title,

                "department": department,

                "location": location,

                "employment_type": employment_type,

                "performance_rating": performance_rating,

                "projects_completed": projects_completed,

                "overtime_hours": overtime_hours,

                "skills_count": skills_count

            }])


            # ------------------------------------------------
            # PREDICT SALARY
            # ------------------------------------------------

            prediction = float(
                model.predict(input_data)[0]
            )


            # Maximum salary = ₹1 crore

            prediction = max(
                0,
                min(prediction, 10000000)
            )


            # ------------------------------------------------
            # CONNECT TO MYSQL
            # ------------------------------------------------

            conn = get_connection()

            cursor = conn.cursor()


            # ------------------------------------------------
            # GENERATE NEW EMPLOYEE ID
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT COALESCE(MAX(employee_id), 1000) + 1
                FROM employees
                """
            )

            employee_id = cursor.fetchone()[0]


            # ------------------------------------------------
            # INSERT EMPLOYEE
            # ------------------------------------------------

            employee_query = """
                INSERT INTO employees
                (
                    employee_id,
                    name,
                    age,
                    gender,
                    education,
                    experience_years,
                    job_title,
                    department,
                    location,
                    employment_type
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            cursor.execute(
                employee_query,
                (
                    employee_id,
                    name,
                    age,
                    gender,
                    education,
                    experience_years,
                    job_title,
                    department,
                    location,
                    employment_type
                )
            )


            # ------------------------------------------------
            # INSERT PERFORMANCE
            # ------------------------------------------------

            performance_query = """
                INSERT INTO employee_performance
                (
                    employee_id,
                    performance_rating,
                    projects_completed,
                    overtime_hours,
                    skills_count
                )
                VALUES
                (
                    %s, %s, %s, %s, %s
                )
            """

            cursor.execute(
                performance_query,
                (
                    employee_id,
                    performance_rating,
                    projects_completed,
                    overtime_hours,
                    skills_count
                )
            )


            # ------------------------------------------------
            # INSERT PREDICTION
            # ------------------------------------------------

            prediction_query = """
                INSERT INTO salary_predictions
                (
                    employee_id,
                    predicted_salary,
                    model_name
                )
                VALUES
                (
                    %s, %s, %s
                )
            """

            cursor.execute(
                prediction_query,
                (
                    employee_id,
                    prediction,
                    "Random Forest Regression"
                )
            )


            # ------------------------------------------------
            # SAVE TO DATABASE
            # ------------------------------------------------

            conn.commit()


            # ------------------------------------------------
            # RESULT DATA
            # ------------------------------------------------

            employee = {

                "employee_id": employee_id,

                "name": name,

                "age": age,

                "gender": gender,

                "education": education,

                "experience_years": experience_years,

                "job_title": job_title,

                "department": department,

                "location": location,

                "employment_type": employment_type,

                "performance_rating": performance_rating,

                "projects_completed": projects_completed,

                "overtime_hours": overtime_hours,

                "skills_count": skills_count

            }


        except Exception as e:

            error = str(e)

            if conn:
                conn.rollback()


        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()


    return render_template(
        "index.html",
        employee=employee,
        prediction=prediction,
        error=error
    )


# ==========================================================
# START FLASK
# ==========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )