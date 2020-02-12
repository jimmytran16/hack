class Student:
# func to check to compare the grade of the student and then return the right bootstrap class for color of the bar graph
    def checkGradeType(grade):
        print(grade)
        if float(grade) < 60.0:
            return 'danger'
        elif float(grade) > 80.0:
            return 'success'
        elif float(grade) < 70.0 and float(grade) > 60.0:
            return 'warning'
        elif float(grade) < 80.0 and float(grade) > 70.0:
            return 'info'

    # func passing in grade and determining the hours needed to study in a day
    # # returns a list of [hour]
    def checkHours(grade):
        if float(grade) >= 90:
            return 0
        elif float(grade) > 80 and float(grade) < 90:
            return 30
        elif float(grade) >= 70 and float(grade) <= 80:
            return 45
        elif float(grade) < 70:
            return 60
        return

    # func for free time
    def freeTime(hour_list):
        total_free = 360
        for i in hour_list:
            total_free = total_free - float(i)
        return total_free
        # func to get the student hour requirements based on their grades and store into a list
    def getStudentHours(student_data,student_teacher):
        list = []
        list.append(Student.checkHours(student_data[2]))  # english
        list.append(Student.checkHours(student_data[3]))  # math
        list.append(Student.checkHours(student_data[4]))  # science
        list.append(Student.checkHours(student_data[5]))  # history
        list.append(Student.freeTime(list))  # free time
        list.append(student_data[0])  # name
        list.append(student_teacher)  # teacher
        return list
