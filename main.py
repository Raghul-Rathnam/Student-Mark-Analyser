import mysql.connector
import csv

DB_NAME = 'school'
TABLE_NAME = 'student'
SUBJECTS = ['phy', 'chem', 'maths', 'eng', 'cs']

def get_db_credentials():
    host = input("MySQL Host : ") 
    user = input("MySQL User : ")
    pwd = input("MySQL Password : ")
    return host, user, pwd

def connect_db(host, user, pwd):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=pwd)
        if conn.is_connected():
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS school ")
            cur.execute(f"USE school")
            cur.execute(f"""CREATE TABLE IF NOT EXISTS student (
                rollno INT PRIMARY KEY,
                name VARCHAR(50),
                phy INT, chem INT, maths INT, eng INT, cs INT,
                total INT, avg FLOAT, grade VARCHAR(2))""")
            conn.commit()
            return conn
    except mysql.connector.Error as e:
        print('Database connection failed:', e)
    return None

def calc_total_avg_grade(marks):
    total = sum(marks)
    avg = total / len(marks)
    if avg >= 90:
        g = 'A+'
    elif avg >= 80:
        g = 'A'
    elif avg >= 70:
        g = 'B'
    elif avg >= 60:
        g = 'C'
    elif avg >= 50:
        g = 'D'
    else:
        g = 'F'
    return total, round(avg,2), g

def input_marks():
    marks = []
    for s in SUBJECTS:
        while True:
            try:
                m = int(input(f'Enter marks for {s.upper()}: '))
                if 0 <= m and m <= 100:
                    marks.append(m)
                    break
                else:
                    print('Enter value between 0 and 100.')
            except ValueError:
                print('Enter a valid number.')
    return marks

def add_student(conn):
    cur = conn.cursor()
    try:
        roll = int(input('Enter Roll No: '))
    except ValueError:
        print("Invalid roll number.")
        return
    cur.execute(f"SELECT * FROM student WHERE rollno=%s", (roll,))
    if cur.fetchone():
        print('Roll number already exists!')
        return
    name = input('Enter Name: ').strip()
    if not name:
        print("Name cannot be empty.")
        return
    marks = input_marks()
    total, avg, grade = calc_total_avg_grade(marks)
    cur.execute(f"""INSERT INTO student VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (roll, name, *marks, total, avg, grade))
    conn.commit()
    print('Student added successfully.')

def display_all(conn):
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM student ORDER BY rollno')
    data = cur.fetchall()
    if not data:
        print('No records found.')
        return
    print(f"{'Roll':<6}{'Name':<20}{'Phy':>6}{'Chem':>6}{'Maths':>7}{'Eng':>6}{'CS':>6}{'Total':>8}{'Avg':>8}{'Grade':>7}")
    print('-'*90)
    for r in data:
        print(f"{r[0]:<6}{r[1]:<20}{r[2]:>6}{r[3]:>6}{r[4]:>7}{r[5]:>6}{r[6]:>6}{r[7]:>8}{r[8]:>8}{r[9]:>7}")

def search_student(conn):
    cur = conn.cursor()
    try:
        roll = int(input('Enter Roll No to search: '))
    except ValueError:
        print("Invalid roll number.")
        return
    cur.execute(f'SELECT * FROM student WHERE rollno=%s', (roll,))
    r = cur.fetchone()
    if r:
        print('\nRoll No:', r[0])
        print('Name   :', r[1])
        for i,s in enumerate(SUBJECTS):
            print(f'{s.upper():6}: {r[2+i]}')
        print('Total  :', r[7])
        print('Average:', r[8])
        print('Grade  :', r[9])
    else:
        print('Student not found.')

def update_student(conn):
    cur = conn.cursor()
    try:
        roll = int(input('Enter Roll No to update: '))
    except ValueError:
        print("Invalid roll number.")
        return
    cur.execute(f'SELECT * FROM student WHERE rollno=%s', (roll,))
    row = cur.fetchone()
    if not row:
        print('Record not found!')
        return
    name = input(f'Enter new name [{row[1]}]: ').strip() or row[1]
    print('Enter new marks :')
    new_marks = []
    for i,s in enumerate(SUBJECTS):
        while True:
            val = input(f'{s.upper()} (current {row[2+i]}): ').strip()
            if val == '':
                new_marks.append(row[2+i])
                break
            try:
                m = int(val)
                if 0 <= m <= 100:
                    new_marks.append(m)
                    break
                else:
                    print('Enter value between 0 and 100.')
            except ValueError:
                print('Enter a valid number or leave blank.')
    total, avg, grade = calc_total_avg_grade(new_marks)
    cur.execute(f"""UPDATE student SET name=%s, phy=%s, chem=%s, maths=%s, eng=%s, cs=%s, total=%s, avg=%s, grade=%s WHERE rollno=%s""",
                (name, *new_marks, total, avg, grade, roll))
    conn.commit()
    print('Record updated successfully.')

def delete_student(conn):
    cur = conn.cursor()
    try:
        roll = int(input('Enter Roll No to delete: '))
    except ValueError:
        print("Invalid roll number.")
        return
    confirm = input('Are you sure? (Y/N): ')
    if confirm.lower() != 'y':
        print('Deletion cancelled.')
        return
    cur.execute(f'DELETE FROM {TABLE_NAME} WHERE rollno=%s', (roll,))
    conn.commit()
    print('Record deleted (if existed).')

def analyse(conn):
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM student')
    data = cur.fetchall()
    if not data:
        print('No data to analyse.')
        return
    avgs = [r[8] for r in data]
    class_avg = round(sum(avgs)/len(avgs),2)
    sorted_overall = sorted(data, key=lambda x:x[8], reverse=True)
    top3_overall = sorted_overall[:3]
    subj_avg = {}
    subj_top3 = {}
    subj_lowest = {}
    for i,s in enumerate(SUBJECTS):
        marks = [r[2+i] for r in data]
        subj_avg[s] = round(sum(marks)/len(marks),2)
        sorted_subj = sorted(data, key=lambda x:x[2+i], reverse=True)
        subj_top3[s] = sorted_subj[:3]
        subj_lowest[s] = min(marks)
    passed = [r for r in data if r[9]!='F']
    pass_percent = round(len(passed)/len(data)*100,2)
    grades = {}
    for r in data:
        grades[r[9]] = grades.get(r[9],0)+1
    print('\n--- CLASS ANALYSIS ---')
    print('Total Students:', len(data))
    print('Class Average :', class_avg)
    print('Pass Percentage:', pass_percent,'%')
    print('\nTop 3 Students Overall:')
    for r in top3_overall:
        print(f'{r[1]} (Roll {r[0]}) - Avg {r[8]}')
    print('\nSubject-wise Top 3 & Lowest:')
    for s in SUBJECTS:
        print(f'{s.upper()}: Avg {subj_avg[s]}, Lowest {subj_lowest[s]}')
        for r in subj_top3[s]:
            print(f'  {r[1]} (Roll {r[0]}) - {r[2+SUBJECTS.index(s)]}')
    print('\nGrade Distribution:')
    for g,c in grades.items():
        print(f'{g}: {c}')

def export_csv(conn):
    filename = input('Enter filename to export CSV : ').strip()
    if not filename:
        print('Invalid filename.')
        return
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM student ORDER BY rollno')
    rows = cur.fetchall()
    if not rows:
        print('No data to export.')
        return
    with open(filename,'w',newline='') as f:
        writer = csv.writer(f)
writer.writerow(['rollno','name','phy','chem','maths','eng','cs','total','avg','grade'])
        writer.writerows(rows)
    print(f'Data exported to Student_Mark_Analyser.py')

def import_csv(conn):
    filename = input('Enter filename to import CSV from : ').strip()
    if not filename:
        print('Invalid filename.')
        return
    cur = conn.cursor()
    try:
        with open(filename,'r') as f:
            reader = csv.DictReader(f)
            count = 0
            for r in reader:
                try:
                    marks = [int(r[s]) for s in SUBJECTS]
                except Exception:
                    continue
                total, avg, grade = calc_total_avg_grade(marks)
                cur.execute(f"""REPLACE INTO {TABLE_NAME} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                            (int(r['rollno']), r['name'], *marks, total, avg, grade))
                count += 1
        conn.commit()
        print(f'Data imported from Student_Mark_Analyser.py. Rows processed: {count}')
    except FileNotFoundError:
        print('CSV file not found!')

def menu():
    print('\n===== STUDENT MARK ANALYSER =====')
    print('1. Add Student')
    print('2. Display All')
    print('3. Search Student')
    print('4. Update Student')
    print('5. Delete Student')
    print('6. Analyse Results')
    print('7. Export to CSV')
    print('8. Import from CSV')
    print('9. Exit')

def main():
    host, user, pwd = get_db_credentials()
    conn = connect_db(host, user, pwd)
    if not conn:
        print('Connection failed. Check MySQL settings.')
        return
    while True:
        menu()
        ch = input('Enter choice: ').strip()
        if ch=='1':
            add_student(conn)
        elif ch=='2':
            display_all(conn)
        elif ch=='3':
            search_student(conn)
        elif ch=='4':
            update_student(conn)
        elif ch=='5':
            delete_student(conn)
        elif ch=='6':
            analyse(conn)
        elif ch=='7':
            export_csv(conn)
        elif ch=='8':
            import_csv(conn)
        elif ch=='9':
            print('Exiting...')
            conn.close()
            break
        else:
            print('Invalid choice!')

if __name__=='__main__':
    main()
