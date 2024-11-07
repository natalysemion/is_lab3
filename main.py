import pandas as pd
import random
from tabulate import tabulate


# Завантаження даних із CSV-файлів
def load_data():
    groups = pd.read_csv("groups.csv")
    subjects = pd.read_csv("subjects.csv")
    lecturers = pd.read_csv("lecturers.csv")
    auditoriums = pd.read_csv("auditoriums.csv")
    return groups, subjects, lecturers, auditoriums


# Генерація початкового розкладу з допущенням накладок
def initialize_population(groups, subjects, lecturers, auditoriums, population_size=50):
    population = []
    for _ in range(population_size):
        schedule = []
        for _, group in groups.iterrows():
            group_id = group['group_id']
            for _, subject in subjects[subjects['group_id'] == group_id].iterrows():
                subject_id = subject['subject_id']
                hours = subject['hours_per_semester']
                type_of_class = subject['type']

                while hours > 0:
                    time = random.randint(1, 20)
                    lecturer_id = random.choice(
                        lecturers[lecturers['subject_id'] == subject_id]['lecturer_id'].tolist())
                    auditorium_id = random.choice(auditoriums['auditorium_id'].tolist())
                    schedule.append({
                        'time': time,
                        'group_id': group_id,
                        'lecturer_id': lecturer_id,
                        'auditorium_id': auditorium_id,
                        'subject_id': subject_id,
                        'type_of_class': type_of_class
                    })
                    hours -= 1
        population.append(schedule)
    return population


# Фітнес-функція з допущенням накладок
def calculate_fitness(schedule, groups, lecturers, auditoriums):
    fitness = 0
    time_slots = {}

    # Підрахунок накладок
    for entry in schedule:
        time = entry['time']
        group_id = entry['group_id']
        lecturer_id = entry['lecturer_id']
        auditorium_id = entry['auditorium_id']
        subject_id = entry['subject_id']

        # Перевірка накладок для викладача
        if (time, lecturer_id) in time_slots:
            fitness += 5  # Штраф за конфлікт лектора
        time_slots[(time, lecturer_id)] = True

        # Перевірка накладок для групи
        if (time, group_id) in time_slots:
            fitness += 5  # Штраф за конфлікт групи
        time_slots[(time, group_id)] = True

        # Перевірка накладок для аудиторії
        if (time, auditorium_id) in time_slots:
            fitness += 5  # Штраф за конфлікт аудиторії
        time_slots[(time, auditorium_id)] = True

    return fitness


# Генетичний алгоритм з поступовим усуненням накладок
def genetic_algorithm(groups, subjects, lecturers, auditoriums, generations=100, population_size=50):
    population = initialize_population(groups, subjects, lecturers, auditoriums, population_size)

    for generation in range(generations):
        population = sorted(population, key=lambda x: calculate_fitness(x, groups, lecturers, auditoriums))

        next_generation = population[:10]
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(population[:20], 2)
            child1, child2 = crossover(parent1, parent2)
            next_generation.append(mutate(child1, lecturers, auditoriums))
            if len(next_generation) < population_size:
                next_generation.append(mutate(child2, lecturers, auditoriums))

        population = next_generation
        best_fitness = calculate_fitness(population[0], groups, lecturers, auditoriums)
        print(f"Покоління {generation + 1}: найкращий фітнес = {best_fitness}")

    return population[0]


# Функції для кросовера та мутації, які покращують популяцію
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2


def mutate(schedule, lecturers, auditoriums):
    entry = random.choice(schedule)
    new_time = random.randint(1, 20)
    new_lecturer = random.choice(lecturers[lecturers['subject_id'] == entry['subject_id']]['lecturer_id'].tolist())
    new_auditorium = random.choice(auditoriums['auditorium_id'].tolist())
    mutated_entry = {
        'time': new_time,
        'group_id': entry['group_id'],
        'lecturer_id': new_lecturer,
        'auditorium_id': new_auditorium,
        'subject_id': entry['subject_id'],
        'type_of_class': entry['type_of_class']
    }
    schedule[schedule.index(entry)] = mutated_entry
    return schedule


# Функція для виведення розкладу для конкретного викладача
def get_lecturer_schedule(schedule, lecturer_id):
    lecturer_schedule = [entry for entry in schedule if entry['lecturer_id'] == lecturer_id]
    lecturer_schedule_sorted = sorted(lecturer_schedule, key=lambda x: x['time'])
    return lecturer_schedule_sorted


# Функція для виведення розкладу для конкретної групи
def get_group_schedule(schedule, group_id):
    group_schedule = [entry for entry in schedule if entry['group_id'] == group_id]
    group_schedule_sorted = sorted(group_schedule, key=lambda x: x['time'])
    return group_schedule_sorted


# Функція для виведення розкладу для конкретної аудиторії
def get_auditorium_schedule(schedule, auditorium_id):
    auditorium_schedule = [entry for entry in schedule if entry['auditorium_id'] == auditorium_id]
    auditorium_schedule_sorted = sorted(auditorium_schedule, key=lambda x: x['time'])
    return auditorium_schedule_sorted


# Функція для виведення розкладу у консоль у вигляді таблиці
def print_schedule_table(schedule):
    headers = ["Час", "Група", "Викладач", "Аудиторія", "Предмет", "Тип заняття"]
    table = []
    for entry in schedule:
        table.append(
            [entry['time'], entry['group_id'], entry['lecturer_id'], entry['auditorium_id'], entry['subject_id'],
             entry['type_of_class']])
    print(tabulate(table, headers=headers, tablefmt="grid"))


# Функція для експорту розкладу в CSV
def export_schedule_to_csv(schedule, filename="schedule.csv"):
    schedule_df = pd.DataFrame(schedule)
    schedule_df.to_csv(filename, index=False)
    print(f"Розклад експортовано у файл: {filename}")


# Запуск програми
if __name__ == "__main__":
    groups, subjects, lecturers, auditoriums = load_data()
    optimal_schedule = genetic_algorithm(groups, subjects, lecturers, auditoriums)

    # Приклад використання нових функцій:
    # Розклад для викладача з ID = 1
    lecturer_schedule = get_lecturer_schedule(optimal_schedule, 1)
    print("Розклад викладача 1:")
    print_schedule_table(lecturer_schedule)

    # Розклад для групи з ID = 1
    group_schedule = get_group_schedule(optimal_schedule, 1)
    print("Розклад групи 1:")
    print_schedule_table(group_schedule)

    # Розклад для аудиторії з ID = 101
    auditorium_schedule = get_auditorium_schedule(optimal_schedule, 101)
    print("Розклад аудиторії 101:")
    print_schedule_table(auditorium_schedule)

    # Експорт повного розкладу у CSV
    export_schedule_to_csv(optimal_schedule)
