import sqlite3 


conn = sqlite3.connect('student.db')

cursor = conn.cursor()

table_info = """
CREATE TABLE IF NOT EXISTS STUDENTS(
  ROLL INT PRIMARY KEY NOT NULL,
  NAME VARCHAR(35) NOT NULL,
  CLASS VARCHAR(15) NOT NULL,
  SECTION VARCHAR(2) NOT NULL,
  MARKS INT 
  )
"""

cursor.execute(table_info)

students_records = [
    (1, "Aarav Sharma", "10", "A", 89),
    (2, "Isha Patel", "10", "A", 94),
    (3, "Rohan Mehta", "10", "B", 76),
    (4, "Priya Singh", "10", "B", 82),
    (5, "Kabir Joshi", "9", "A", 91),
    (6, "Ananya Verma", "9", "C", 85),
    (7, "Aditya Rao", "9", "B", 67),
    (8, "Meera Iyer", "8", "A", 95),
    (9, "Sahil Kapoor", "8", "B", 72),
    (10, "Diya Nair", "8", "C", 88),
    (11, "Ritika Deshmukh", "7", "A", 81),
    (12, "Arjun Pillai", "7", "B", 90),
    (13, "Tanya Bansal", "7", "C", 79),
    (14, "Harsh Tiwari", "6", "A", 93),
    (15, "Sneha Reddy", "6", "B", 84),
    (16, "Rajat Malhotra", "6", "C", 77),
    (17, "Manav Chawla", "5", "A", 86),
    (18, "Simran Kaur", "5", "B", 92),
    (19, "Dev Patel", "5", "C", 73),
    (20, "Nisha Gupta", "4", "A", 88)
]

for record in students_records:
  cursor.execute("INSERT INTO STUDENTS VALUES(?, ?, ?, ?, ?)", record)

# Display all record 

data = cursor.execute("SELECT * FROM STUDENTS")

for row in data:
  print(row)

conn.commit()
conn.close()