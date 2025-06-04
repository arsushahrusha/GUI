# -*- coding: utf-8 -*-

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.chdir("c:/work/work/")

data = pd.ExcelFile('./data/courses.xlsx')


arr = ['student', 'groups', 'courses', 'schools',]

if not(all(os.path.exists(f"./data/{name}.pick") for name in arr)):
    for sn in data.sheet_names[1:]:
        exec(f'{sn} = data.parse(sheet_name="{sn}")')
        exec(f'{sn}.to_pickle("./data/{sn}.pick")')

student = pd.read_pickle('./data/student.pick')
groups = pd.read_pickle('./data/groups.pick')
courses = pd.read_pickle('./data/courses.pick')
schools = pd.read_pickle('./data/schools.pick')


#Курсы, на которые ходит ученик
def courses_by_student(student_name, student_df, groups_df, courses_df):
    student_ids = student_df.loc[student_df['Фамилия'] == student_name, 'ID Учащегося'].values
    if len(student_ids) == 0:
        return 'Ученика с такой фамилией не найдено'
    group_ids = student_df.loc[student_df['Фамилия'] == student_name, 'ID Группы'].unique()
    course_ids = groups_df[groups_df['ID Группы'].isin(group_ids)]['ID Курса'].unique()
    course_names = courses_df[courses_df['ID Курса'].isin(course_ids)]['Наименование'].unique()
    return course_names   

#Количество учеников в школе
def amount_of_students_in_school(school_name, student_df, groups_df, courses_df, schools_df):
    schools_ids = schools_df.loc[schools_df['Наименование школы'] == school_name, 'ID Школы'].values
    if len(schools_ids) == 0:
        return 'Такой школы не найдено'
    
    courses_ids = courses_df.loc[courses_df['ID Школы'].isin(schools_ids), 'ID Курса'].unique()
    group_ids = groups_df.loc[groups_df['ID Курса'].isin(courses_ids), 'ID Группы'].unique()
    student_ids = student_df[student_df['ID Группы'].isin(group_ids)]['Фамилия'].unique()
    return len(student_ids)

#Количество учеников на курсе
def amount_of_students_in_course(course, student_df, groups_df, courses_df):
    courses_ids = courses_df.loc[courses_df['Наименование'] == course, 'ID Курса'].values
    if len(courses_ids) == 0:
        return 'Такого курса не найдено'
    group_ids = groups_df.loc[groups_df['ID Курса'].isin(courses_ids)]['ID Группы'].unique()
    student_ids = student_df[student_df['ID Группы'].isin(group_ids)]['Фамилия'].unique()
    return len(student_ids)

#Статистика по курсам
def courses_statistics_report(courses_df, student_df, groups_df):
    stats = []
    for _, course in courses_df.iterrows():
        course_name = course['Наименование']
        course_id = course['ID Курса']
        
        group_ids = groups_df[groups_df['ID Курса'] == course_id]['ID Группы'].unique()
        students_on_course = student_df[student_df['ID Группы'].isin(group_ids)]
        
        stats.append({
            'Курс': course_name,
            'Количество студентов': len(students_on_course),
            'Средняя оценка': round(students_on_course['Итоговая оценка'].mean(), 2),
            'Максимальная оценка': students_on_course['Итоговая оценка'].max(),
            'Минимальная оценка': students_on_course['Итоговая оценка'].min()
        })
    
    return pd.DataFrame(stats)

#Сводная таблица по курсам и школам
def create_pivot_table(student_df, groups_df, courses_df, schools_df):
    student_groups = pd.merge(student_df, groups_df, on='ID Группы', how='inner')
    student_courses = pd.merge(student_groups, courses_df, on='ID Курса', how='inner')
    student_school_courses = pd.merge(student_courses, schools_df, on='ID Школы', how='inner')
    pivot = pd.pivot_table(student_school_courses, values='Итоговая оценка',
                           index='Наименование школы',
                           columns='Наименование',
                           aggfunc=np.mean)

    return pivot

#Лучшие ученики школы (больше или равна 4м оценка)
def best_students_by_school(school_name, student_df, groups_df, courses_df, schools_df, min_grade=4):
    schools_ids = schools_df.loc[schools_df['Наименование школы'] == school_name, 'ID Школы'].values
    if len(schools_ids) == 0:
        return 'Такой школы не найдено'
    
    courses_ids = courses_df.loc[courses_df['ID Школы'].isin(schools_ids), 'ID Курса'].unique()
    group_ids = groups_df.loc[groups_df['ID Курса'].isin(courses_ids), 'ID Группы'].unique()
    best_students = student_df[(student_df['ID Группы'].isin(group_ids)) & 
                              (student_df['Итоговая оценка'] >= min_grade)]
    return best_students[['Фамилия', 'Класс', 'Итоговая оценка']].sort_values('Итоговая оценка', ascending=False)


#Средняя оценка по курсу
def plot_course_mark(course_name, student_df, groups_df, courses_df):
    if course_name not in courses_df['Наименование'].values:
        print("Курс с таким названием не найден")
        return
    course_id = courses_df[courses_df['Наименование'] == course_name]['ID Курса'].iloc[0]
    group_ids = groups_df[groups_df['ID Курса'] == course_id]['ID Группы'].values
    course_students = student_df[student_df['ID Группы'].isin(group_ids)]
    plt.figure(figsize=(10, 6))
    plt.hist(course_students['Итоговая оценка'], bins=5, edgecolor='black')
    plt.title(f'Распределение оценок по курсу {course_name}')
    plt.xlabel('Оценка')
    plt.ylabel('Количество студентов')
    plt.xticks(range(1, 6))
    plt.grid(True)
    plt.show()

#Средняя оценка по школам
def plot_school_marks(student_df, groups_df, courses_df, schools_df):
    students_with_school = pd.merge(student_df, groups_df, on='ID Группы')
    students_with_school = pd.merge(students_with_school, courses_df, on='ID Курса')
    students_with_school = pd.merge(students_with_school, schools_df, on='ID Школы')

    school_performance = students_with_school.groupby('Наименование школы')['Итоговая оценка'].mean()

    plt.figure(figsize=(12, 6))
    school_performance.plot(kind='bar')
    plt.title('Средняя успеваемость по школам')
    plt.ylabel('Средняя оценка')
    plt.ylim(0, 5)
    plt.grid(True)
    plt.show()

#Зависимость оценки от класса
def plot_mark_by_grade(student_df):
    plt.figure(figsize=(12, 6))
    plt.scatter(student_df['Класс'], student_df['Итоговая оценка'], alpha=0.5)
    plt.title('Зависимость оценок от класса')
    plt.xlabel('Класс')
    plt.ylabel('Оценка')
    plt.grid(True)
    plt.show()
    
#Основное меню
def main_menu():
    while True:
        print("\nГЛАВНОЕ МЕНЮ:")
        print("1. Текстовые отчеты")
        print("2. Графические отчеты")
        print("3. Выход")
        
        choice = input("Выберите пункт меню (1-3): ")
        
        if choice == '1':
            text_reports_menu()
        elif choice == '2':
            graphic_reports_menu()
        elif choice == '3':
            print("Ну и до свидания!")
            break
        else:
            print("Неверный ввод. Пожалуйста, выберите 1, 2 или 3.")
            
#Меню текстовых отчетов
def text_reports_menu():
    while True:
        print("\nТЕКСТОВЫЕ ОТЧЕТЫ:")
        print("1. Отчет по курсам, посещаемых учеником")
        print("2. Отчет по колучеству учеников в школе")
        print("3. Отчет по количесвту учеников на курсе")
        print("4. Статистика по всем курсам")
        print("5. Сводная таблица по курсам и школам")
        print("6. Лучшие ученики в школе")
        print("7. Назад")
        
        choice = input("Выберите пункт меню (1-7): ")
        
        if choice == '1':
            print("\nДоступные ученики:", *student['Фамилия'].unique())
            name = input("Введите фамилию ученика: ")
            courses_list = courses_by_student(name, student, groups, courses)
            if isinstance(courses_list, str):
                print(courses_list)
            else:
                print(f"\nКурсы, посещаемые учеником {name}:")
                for course in courses_list:
                    print(f"- {course}")    
        elif choice == '2':
            print("\nДоступные школы:", *schools['Наименование школы'].unique())
            school = input("Введите название школы: ")
            num_students = amount_of_students_in_school(school, student, groups, courses, schools)
            print(f"\nКоличество учащихся в школе {school}: {num_students}")
        elif choice == '3':
            print("\nДоступные курсы:", *courses['Наименование'].unique())
            course = input("Введите название курса: ")
            num_students = amount_of_students_in_course(course, student, groups, courses)
            print(f"\nКоличество учащихся на курсе {course}: {num_students}")
        elif choice == '4':
            print("\nСтатистика по всем курсам:")
            stats_df = courses_statistics_report(courses, student, groups)
            print(stats_df.to_markdown())
        elif choice == '5':
            pivot = create_pivot_table(student, groups, courses, schools)
            print("\nСводная таблица по курсам и школам:")
            print(pivot.to_markdown())
        elif choice == '6':
            print("\nДоступные школы:", *schools['Наименование школы'].unique())
            school_name = input("Введите название школы: ")
            best_students = best_students_by_school(school_name, student, groups, courses, schools)
            print(f"\nЛучшие ученики школы {school_name}: {best_students}")    
        elif choice == '7':
            break
        else:
            print("Неверный ввод. Пожалуйста, выберите 1-7.")
            
#Меню графических отчетов
def graphic_reports_menu():
    while True:
        print("\nГРАФИЧЕСКИЕ ОТЧЕТЫ:")
        print("1. Распределение оценок по курсу")
        print("2. Успеваемость по школам")
        print("3. Диаграмма рассеивания оценок по классам")
        print("4. Назад")
        
        choice = input("Выберите пункт меню (1-4): ")
        
        if choice == '1':
            print("\nДоступные курсы:", *courses['Наименование'].unique())
            course = input("Введите название курса: ")
            plot_course_mark(course, student, groups, courses)
            
        elif choice == '2':
            plot_school_marks(student, groups, courses, schools)
            
            
        elif choice == '3':
            plot_mark_by_grade(student)
            
        elif choice == '4':
            break
        else:
            print("Неверный ввод. Пожалуйста, выберите 1-4.")

#main_menu()

if __name__ == "__main__":
    # Автоматический запуск GUI
    import tkinter as tk
    from gui import ReportApp
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()