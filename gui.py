
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import database  # Импорт функций из database.py


class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ успеваемости")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")

        # Настройка стилей
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#ded8d8")
        #self.style.configure("TButton", font=("Arial", 10), padding=6, background="#ded8d8", foreground="#ffffff")
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure("TCombobox", font=("Arial", 10))
        #self.style.map("TButton", background=[("active", "#ded8d8")])
        
        #self.style = ttk.Style()
        self.style.configure("Custom.TButton", font=("Arial", 10), padding=6,
                             background="#5db0ff", foreground="#ffffff") # Задаем цвет фона здесь
        self.style.map("Custom.TButton",
                       background=[("active", "#7ec1ff"), ("pressed", "#3d90df")], # Задаем цвета фона для active и pressed
                       foreground=[("active", "#ffffff"), ("pressed", "#ffffff")])

        # Вкладки
        self.tab_control = ttk.Notebook(root)
        
        # Вкладка "Графические отчеты"
        self.graphic_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.graphic_tab, text="Графические отчеты")
        
        # Вкладка "Текстовые отчеты"
        self.text_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.text_tab, text="Текстовые отчеты")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Инициализация вкладок
        self.init_graphic_tab()
        self.init_text_tab()

    def init_graphic_tab(self):
        frame = ttk.Frame(self.graphic_tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Область для графика
        self.graph_frame = ttk.Frame(frame)
        self.graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=10)

        # Кнопки выбора графиков
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X)

        btn1 = ttk.Button(btn_frame, text="Распределение оценок по курсу", 
                         command=self.show_course_grades)
        btn1.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        btn2 = ttk.Button(btn_frame, text="Успеваемость по школам", 
                         command=self.show_school_performance)
        btn2.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        btn3 = ttk.Button(btn_frame, text="Зависимость оценок от класса", 
                         command=self.show_grade_dependency)
        btn3.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

    def init_text_tab(self):
        frame = ttk.Frame(self.text_tab)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Кнопки выбора текстовых отчетов
        btn1 = ttk.Button(frame, text="Курсы ученика", 
                         command=self.show_student_courses)
        btn1.pack(pady=5, fill="x")

        btn2 = ttk.Button(frame, text="Количество учеников в школе", 
                         command=self.show_school_students)
        btn2.pack(pady=5, fill="x")

        btn3 = ttk.Button(frame, text="Количество учеников на курсе", 
                         command=self.show_course_students)
        btn3.pack(pady=5, fill="x")

        btn4 = ttk.Button(frame, text="Статистика по курсам", 
                         command=self.show_course_stats)
        btn4.pack(pady=5, fill="x")

        btn5 = ttk.Button(frame, text="Сводная таблица", 
                         command=self.show_pivot_table)
        btn5.pack(pady=5, fill="x")

        btn6 = ttk.Button(frame, text="Лучшие ученики школы", 
                         command=self.show_best_students)
        btn6.pack(pady=5, fill="x")

    # --- Методы для графических отчетов ---
    def clear_graph_frame(self):
        """Очищает область с графиком"""
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def show_course_grades(self):
        self.clear_graph_frame()
        
        # Создаем элементы управления
        control_frame = ttk.Frame(self.graph_frame)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        label = ttk.Label(control_frame, text="Выберите курс:")
        label.pack(side=tk.LEFT, padx=5)

        course_var = tk.StringVar()
        courses = database.courses['Наименование'].unique()
        combobox = ttk.Combobox(control_frame, textvariable=course_var, values=courses)
        combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        def plot():
            course = course_var.get()
            if not course:
                messagebox.showerror("Ошибка", "Выберите курс!")
                return
            
            # Получаем данные
            course_id = database.courses[database.courses['Наименование'] == course]['ID Курса'].iloc[0]
            group_ids = database.groups[database.groups['ID Курса'] == course_id]['ID Группы'].values
            grades = database.student[database.student['ID Группы'].isin(group_ids)]['Итоговая оценка']

            # Создаем график
            fig = plt.Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Гистограмма
            ax.hist(grades, bins=5, range=(1, 6), edgecolor='black', align='left')
            ax.set_title(f'Распределение оценок по курсу {course}')
            ax.set_xlabel('Оценка')
            ax.set_ylabel('Количество студентов')
            ax.set_xticks(range(1, 6))
            ax.grid(True)

            # Встраиваем график в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        btn = ttk.Button(control_frame, text="Построить график", command=plot)
        btn.pack(side=tk.LEFT, padx=5)

    def show_school_performance(self):
        self.clear_graph_frame()
        
        # Получаем данные
        students_with_school = pd.merge(database.student, database.groups, on='ID Группы')
        students_with_school = pd.merge(students_with_school, database.courses, on='ID Курса')
        students_with_school = pd.merge(students_with_school, database.schools, on='ID Школы')

        school_performance = students_with_school.groupby('Наименование школы')['Итоговая оценка'].mean()

        # Создаем график
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Столбчатая диаграмма
        school_performance.plot(kind='bar', ax=ax, color='#4CAF50')
        ax.set_title('Средняя успеваемость по школам')
        ax.set_ylabel('Средняя оценка')
        ax.set_ylim(0, 5)
        ax.grid(True)

        # Встраиваем график
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_grade_dependency(self):
        self.clear_graph_frame()
        
        # Создаем график
        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Диаграмма рассеивания
        ax.scatter(database.student['Класс'], database.student['Итоговая оценка'], alpha=0.5, color='#2196F3')
        ax.set_title('Зависимость оценок от класса')
        ax.set_xlabel('Класс')
        ax.set_ylabel('Оценка')
        ax.grid(True)

        # Встраиваем график
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # --- Текстовые отчеты ---
    def show_student_courses(self):
        window = tk.Toplevel(self.root)
        window.title("Курсы ученика")
        
        label = ttk.Label(window, text="Введите фамилию ученика:")
        label.pack(pady=10)
        
        entry = ttk.Entry(window)
        entry.pack(pady=5, padx=10, fill="x")
        
        def show():
            name = entry.get()
            if not name:
                messagebox.showerror("Ошибка", "Введите фамилию!")
                return
            
            result = database.courses_by_student(name, database.student, database.groups, database.courses)
            
            if isinstance(result, str):
                messagebox.showinfo("Результат", result)
            else:
                text = "\n".join([f"- {course}" for course in result])
                messagebox.showinfo(f"Курсы ученика {name}", text)
        
        btn = ttk.Button(window, text="Показать курсы", command=show)
        btn.pack(pady=10)
    
    def show_school_students(self):
        window = tk.Toplevel(self.root)
        window.title("Количество учеников в школе")
        
        label = ttk.Label(window, text="Выберите школу:")
        label.pack(pady=10)
        
        school_var = tk.StringVar()
        schools = database.schools['Наименование школы'].unique()
        combobox = ttk.Combobox(window, textvariable=school_var, values=schools)
        combobox.pack(pady=5, padx=10, fill="x")
        
        def show():
            school = school_var.get()
            if not school:
                messagebox.showerror("Ошибка", "Выберите школу!")
                return
            
            result = database.amount_of_students_in_school(
                school, database.student, database.groups, 
                database.courses, database.schools
            )
            messagebox.showinfo("Результат", f"Количество учеников: {result}")
        
        btn = ttk.Button(window, text="Показать", command=show)
        btn.pack(pady=10)
    
    # (Аналогично реализуются остальные текстовые отчеты...)
    def show_course_students(self):
        pass
    
    def show_course_stats(self):
        pass
    
    def show_pivot_table(self):
        pass
    
    def show_best_students(self):
        pass

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()