import pandas as pd
import mysql.connector

# Read CSV
df = pd.read_csv(r"C:\Users\HP\Downloads\employee_salary.csv")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root@789",
    database="employee_salary_db"
)

cursor = conn.cursor()

# Insert employee data
employee_query = """
INSERT INTO employees
(employee_id, age, gender, education, experience_years,
 job_title, department, location, employment_type)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

for _, row in df.iterrows():
    cursor.execute(employee_query, (
        int(row["employee_id"]),
        int(row["age"]),
        row["gender"],
        row["education"],
        int(row["experience_years"]),
        row["job_title"],
        row["department"],
        row["location"],
        row["employment_type"]
    ))

# Insert performance data
performance_query = """
INSERT INTO employee_performance
(employee_id, performance_rating, projects_completed,
 overtime_hours, skills_count)
VALUES (%s,%s,%s,%s,%s)
"""

for _, row in df.iterrows():
    cursor.execute(performance_query, (
        int(row["employee_id"]),
        float(row["performance_rating"]),
        int(row["projects_completed"]),
        int(row["overtime_hours"]),
        int(row["skills_count"])
    ))

conn.commit()

print("Data imported successfully!")
print(f"Employees inserted: {len(df)}")

cursor.close()
conn.close()