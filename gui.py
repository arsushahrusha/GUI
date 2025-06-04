import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Text, Scrollbar, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import database


class ReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Анализ успеваемости")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        self.root.configure(bg='#ffffff')
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 12), padding=6, background="#ebfeff")
        self.style.configure("Custom.TRadiobutton",
                             background='#ebfeff',
                             foreground='black',
                             font=('Arial', 12))

        self.style.map('Custom.TRadiobutton',
                       background=[('active', '#d6f7ff'),
                                   ('selected', '#c8fbfe')],
                       foreground=[('selected', 'green')])
        self.style.configure("Custom.TLabel",
                background="#ebfeff",
                font=("Arial", 12))
        self.style.configure("Custom.TCombobox",
                font=("Arial", 12))
        self.style.configure('TFrame', background='#ebfeff')
        self.tab_control = ttk.Notebook(root)
        self.style.configure('TPanedwindow', borderwidth=0, relief='flat')
        self.graphic_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.graphic_tab, text="Графические отчеты")

        self.text_tab = ttk.Frame(self.tab_control)
        self.reference_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.text_tab, text="Текстовые отчеты")
        self.tab_control.add(self.reference_tab, text="Справочники")


        self.tab_control.pack(expand=1, fill="both")

        self.init_graphic_tab()
        self.init_text_tab()
        self.init_reference_tab()

    def init_graphic_tab(self):
        frame = ttk.Frame(self.graphic_tab, style="TFrame")
        frame.pack(fill="both", expand=True, padx=20, pady=2)

        paned = ttk.Panedwindow(frame, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        radio_frame = ttk.Frame(paned, style="TFrame")
        paned.add(radio_frame, weight=1)

        self.report_type = tk.StringVar()
        self.report_type.set(None)

        ttk.Radiobutton(radio_frame, text="Распределение оценок по курсу",
                          variable=self.report_type, value="course_grades",
                          command=self.show_selected_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(radio_frame, text="Успеваемость по школам",
                          variable=self.report_type, value="school_performance",
                          command=self.show_selected_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(radio_frame, text="Зависимость оценок от класса",
                          variable=self.report_type, value="grade_dependency",
                          command=self.show_selected_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=2)

        self.control_frame = ttk.Frame(radio_frame, style="TFrame")
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        self.graph_frame = ttk.Frame(paned, style="TFrame")
        paned.add(self.graph_frame, weight=3)

        self.save_button_frame = ttk.Frame(frame, style="TFrame")
        self.save_button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    def init_text_tab(self):
        frame = ttk.Frame(self.text_tab,  style="TFrame")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Button(frame, text="Курсы ученика",
                 command=self.show_student_courses).pack(fill="x", pady=5)

        ttk.Button(frame, text="Количество учеников в школе",
                 command=self.show_school_students).pack(fill="x", pady=5)

        ttk.Button(frame, text="Количество учеников на курсе",
                 command=self.show_course_students).pack(fill="x", pady=5)

    def init_reference_tab(self):
        frame = ttk.Frame(self.reference_tab,  style="TFrame")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.reference_report_var = tk.StringVar()
        self.reference_report_var.set(None)
        ttk.Radiobutton(frame, text="Общая таблица",
                          variable=self.reference_report_var, value="all_data",
                          command=self.show_reference_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(frame, text="Статистика по курсам",
                          variable=self.reference_report_var, value="course_stats",
                          command=self.show_reference_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(frame, text="Сводная таблица",
                          variable=self.reference_report_var, value="pivot_table",
                          command=self.show_reference_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=5)

        ttk.Radiobutton(frame, text="Лучшие ученики школы",
                          variable=self.reference_report_var, value="best_students",
                          command=self.show_reference_report, style="Custom.TRadiobutton").pack(anchor=tk.W, pady=5)

        self.input_frame = ttk.Frame(frame, style="TFrame")
        self.input_frame.pack(side="top",fill="x")

        self.reference_report_output_frame = ttk.Frame(frame, style="TFrame")
        self.reference_report_output_frame.pack(side=tk.TOP, fill="both", expand=True)

    def show_selected_report(self):
        selected_report = self.report_type.get()
        self.clear_control_frame()
        self.clear_graph_frame()
        self.clear_save_button()

        if selected_report == "course_grades":
            self.show_course_grades()
        elif selected_report == "school_performance":
            self.show_school_performance()
        elif selected_report == "grade_dependency":
            self.show_grade_dependency()
        self.show_save_button()

    def show_reference_report(self):
        report_type = self.reference_report_var.get()
        self.clear_reference_report_output()
        self.clear_input_frame()

        if report_type == "course_stats":
            self.show_course_stats()
        elif report_type == "pivot_table":
            self.show_pivot_table()
        elif report_type == "best_students":
            self.show_best_students()
        elif report_type == "all_data":
            self.show_all_data()
            

    def clear_reference_report_output(self):
        for widget in self.reference_report_output_frame.winfo_children():
            widget.destroy()

    def clear_graph_frame(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

    def clear_control_frame(self):
        for widget in self.control_frame.winfo_children():
            widget.destroy()

    def clear_input_frame(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

    def clear_save_button(self):
        for widget in self.save_button_frame.winfo_children():
            widget.destroy()

    def clean_course_name(self, course_name):
        chars_to_remove = "[]'\"\\"
        cleaned_name = "".join(c for c in course_name if c not in chars_to_remove)
        return cleaned_name

    def clean_school_name(self, school_name):
        chars_to_remove = "[]'\"\\"
        cleaned_name = "".join(c for c in school_name if c not in chars_to_remove)
        return cleaned_name


    def show_course_grades(self):
        label = ttk.Label(self.control_frame, text="Выберите курс:", style="Custom.TLabel")
        label.pack(side=tk.LEFT, padx=5)

        course_var = tk.StringVar()
        courses = database.courses['Наименование'].unique()

        cleaned_courses = [self.clean_course_name(course) for course in courses]

        combobox = ttk.Combobox(self.control_frame, textvariable=course_var, values=cleaned_courses, style="Custom.TCombobox")
        combobox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        def plot():
            self.clear_graph_frame()
            course = course_var.get()
            if not course:
                messagebox.showerror("Ошибка", "Выберите курс!")
                return

            original_course = next(
                (c for c in courses if self.clean_course_name(c) == course),
                None
            )

            if original_course is None:
                messagebox.showerror("Ошибка", "Курс не найден в базе данных.")
                return

            course_id = database.courses[database.courses['Наименование'] == original_course]['ID Курса'].iloc[0]
            group_ids = database.groups[database.groups['ID Курса'] == course_id]['ID Группы'].values
            grades = database.student[database.student['ID Группы'].isin(group_ids)]['Итоговая оценка']

            fig = plt.Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)

            ax.hist(grades, bins=5, range=(1, 6), edgecolor='black', align='left')
            ax.set_title(f'Распределение оценок по курсу {course}')
            ax.set_xlabel('Оценка')
            ax.set_ylabel('Количество студентов')
            ax.set_xticks(range(1, 6))
            ax.grid(True)

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.current_figure = fig
        btn = ttk.Button(self.control_frame, text="Построить график", command=plot, style="TButton")
        btn.pack(side=tk.LEFT, padx=5)

    def show_school_performance(self):
        self.clear_control_frame()
        self.clear_graph_frame()

        students_with_school = pd.merge(database.student, database.groups, on='ID Группы')
        students_with_school = pd.merge(students_with_school, database.courses, on='ID Курса')
        students_with_school = pd.merge(students_with_school, database.schools, on='ID Школы')

        school_performance = students_with_school.groupby('Наименование школы')['Итоговая оценка'].mean()

        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        school_performance.plot(kind='bar', ax=ax, color='#4CAF50')
        ax.set_title('Средняя успеваемость по школам')
        ax.set_ylabel('Средняя оценка')
        ax.set_ylim(0, 5)
        ax.grid(True)

        ax.tick_params(axis='x', rotation=45)

        fig.subplots_adjust(left=0.1, bottom=0.35, right=0.9, top=0.9, wspace=0, hspace=0)
        self.current_figure = fig
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_grade_dependency(self):
        self.clear_control_frame()
        self.clear_graph_frame()

        fig = plt.Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.scatter(database.student['Класс'], database.student['Итоговая оценка'], alpha=0.5, color='#2196F3')
        ax.set_title('Зависимость оценок от класса')
        ax.set_xlabel('Класс')
        ax.set_ylabel('Оценка')
        ax.grid(True)
        self.current_figure = fig

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def show_student_courses(self):
        window = tk.Toplevel(self.root)
        window.title("Курсы ученика")

        label = ttk.Label(window, text="Введите фамилию ученика:", style = "Custom.TLabel")
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

        btn = ttk.Button(window, text="Показать курсы", command=show, style='TButton')
        btn.pack(pady=10)

    def show_school_students(self):
        window = tk.Toplevel(self.root)
        window.title("Количество учеников в школе")

        label = ttk.Label(window, text="Выберите школу:", style = "Custom.TLabel")
        label.pack(pady=10)

        school_var = tk.StringVar()
        schools = database.schools['Наименование школы'].unique()

        cleaned_schools = [self.clean_school_name(school) for school in schools]
        combobox = ttk.Combobox(window, textvariable=school_var, values=cleaned_schools, style = "Custom.TCombobox")
        combobox.pack(pady=5, padx=10, fill="x")

        def show():
            school = school_var.get()
            if not school:
                messagebox.showerror("Ошибка", "Выберите школу!")
                return

            original_school = next(
                (s for s in schools if self.clean_school_name(s) == school),
                None
            )

            if original_school is None:
                messagebox.showerror("Ошибка", "Школа не найдена в базе данных.")
                return

            result = database.amount_of_students_in_school(
                original_school, database.student, database.groups,
                database.courses, database.schools
            )
            messagebox.showinfo("Результат", f"Количество учеников: {result}")

        btn = ttk.Button(window, text="Показать", command=show, style='TButton')
        btn.pack(pady=10)

    def show_course_students(self):
        window = tk.Toplevel(self.root)
        window.title("Количество учеников на курсе")

        label = ttk.Label(window, text="Выберите курс:", style = "Custom.TLabel")
        label.pack(pady=10)

        course_var = tk.StringVar()
        courses = database.courses['Наименование'].unique()
        combobox = ttk.Combobox(window, textvariable=course_var, values=courses, style = "Custom.TCombobox")
        combobox.pack(pady=5, padx=10, fill="x")

        def show():
            course = course_var.get()
            if not course:
                messagebox.showerror("Ошибка", "Выберите курс!")
                return

            result = database.amount_of_students_in_course(
                course, database.student, database.groups,
                database.courses
            )
            messagebox.showinfo("Результат", f"Количество учеников: {result}")

        btn = ttk.Button(window, text="Показать", command=show, style='TButton')
        btn.pack(pady=10)
    def show_all_data(self):
        self.clear_reference_report_output()

        text_area = Text(self.reference_report_output_frame, wrap="none")
        scrollbar_y = Scrollbar(self.reference_report_output_frame, command=text_area.yview)
        scrollbar_x = Scrollbar(self.reference_report_output_frame, orient="horizontal", command=text_area.xview)

        text_area.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        text_area.pack(expand=True, fill="both")

        text_area.insert("1.0", database.student.to_string())
        text_area.configure(state="disabled")
    def show_course_stats(self):
        self.clear_reference_report_output()

        stats_df = database.courses_statistics_report(database.courses, database.student, database.groups)

        text_area = Text(self.reference_report_output_frame, wrap="none")
        scrollbar_y = Scrollbar(self.reference_report_output_frame, command=text_area.yview)
        scrollbar_x = Scrollbar(self.reference_report_output_frame, orient="horizontal", command=text_area.xview)

        text_area.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        text_area.pack(expand=True, fill="both")

        text_area.insert("1.0", stats_df.to_string())
        text_area.configure(state="disabled")


    def show_pivot_table(self):
        self.clear_reference_report_output()

        pivot = database.create_pivot_table(database.student, database.groups, database.courses, database.schools)

        text_area = Text(self.reference_report_output_frame, wrap="none")
        scrollbar_y = Scrollbar(self.reference_report_output_frame, command=text_area.yview)
        scrollbar_x = Scrollbar(self.reference_report_output_frame, orient="horizontal", command=text_area.xview)

        text_area.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        text_area.pack(expand=True, fill="both")

        text_area.insert("1.0", pivot.to_string())
        text_area.configure(state="disabled")

    def show_best_students(self):
        def show():
            
            school_name = school_var.get()
            if not school_name:
                messagebox.showerror("Ошибка", "Выберите школу!")
                return

            original_school = next(
                (s for s in schools if self.clean_school_name(s) == school_name),
                None
            )

            if original_school is None:
                messagebox.showerror("Ошибка", "Школа не найдена в базе данных.")
                return
            try:
                self.clear_reference_report_output()
                best_students = database.best_students_by_school(original_school, database.student, database.groups, database.courses, database.schools)


                text_area = Text(self.reference_report_output_frame, wrap="none")
                scrollbar_y = Scrollbar(self.reference_report_output_frame, command=text_area.yview)
                scrollbar_x = Scrollbar(self.reference_report_output_frame, orient="horizontal", command=text_area.xview)

                text_area.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

                scrollbar_y.pack(side="right", fill="y")
                scrollbar_x.pack(side="bottom", fill="x")
                text_area.pack(expand=True, fill="both")

                text_area.insert("1.0", best_students.to_string())
                text_area.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        self.clear_reference_report_output()
        self.clear_input_frame()

        label = ttk.Label(self.input_frame, text="Выберите школу:", style = "Custom.TLabel")
        label.pack(side="left",pady=10)

        school_var = tk.StringVar()
        schools = database.schools['Наименование школы'].unique()
        cleaned_schools = [self.clean_school_name(school) for school in schools]

        combobox = ttk.Combobox(self.input_frame, textvariable=school_var, values=cleaned_schools, style = "Custom.TCombobox")
        combobox.pack(side="left",pady=5, padx=10, fill="x")
        btn = ttk.Button(self.input_frame, text="Показать", command=show, style='TButton')
        btn.pack(side="left",pady=10)

    def show_save_button(self):
        def save_plot():
            if hasattr(self, 'current_figure') and self.current_figure:
                filename = filedialog.asksaveasfilename(defaultextension=".png",
                                                       filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
                if filename:
                    self.current_figure.savefig(filename)  # Сохраняем сохраненную фигуру
                    messagebox.showinfo("Сохранено", f"График сохранен как {filename}")
            else:
                messagebox.showinfo("Ошибка", "Нет графика для сохранения.")

        for widget in self.save_button_frame.winfo_children():
            widget.destroy()

        save_button = ttk.Button(self.save_button_frame, text="Сохранить", command=save_plot, style="TButton")
        save_button.pack(side="left",pady=5, padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = ReportApp(root)
    root.mainloop()