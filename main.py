import mysql.connector
from utildb import utildb
from managedb import managedb
from student import Student
from course import Course

db = managedb()

student = Student()
student.id = 1
student.name = 'Dmitry'
student.course_id = 500

course = Course()
course.course_id = 500
course.course_name = 'IOT'

# db.execute(utildb.insert('course_table', course))
# db.execute(utildb.insert('student_table', student))

student.id = 2
student.name = 'Max'
student.course_id = 600

course.course_id = 600
course.course_name = 'SQL'

# db.execute(utildb.insert('course_table', course))
# db.execute(utildb.insert('student_table', student))

student.id = 3
student.name = 'Max'
student.course_id = 700

course.course_id = 700
course.course_name = 'AZURE'

# db.execute(utildb.insert('course_table', course))
# db.execute(utildb.insert('student_table', student))

# print(db.query(utildb.select_all_where('student_table', 'id',1)))

# db.execute(utildb.delete_all('student_table'))
# db.execute(utildb.delete_all('course_table'))
# db.execute(utildb.delete_by_id('student_table',3))

# db.execute(utildb.update_by_id('student_table',student,1))

# print(db.query(utildb.select_by_id('student_table',1)))
print(db.query(utildb.select_all('student_table')))
# print(db.query(utildb.select_all('course_table')))

db.die()