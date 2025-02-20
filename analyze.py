import pandas as pd
from fuzzywuzzy import fuzz

# Карточка профессии (пример)
job_card = {
    "title": "Data Analyst",
    "skills": ["SQL", "Python", "Pandas", "Excel", "Power BI"],
    "experience": "2+ года работы в аналитике данных"
}

# Функция анализа резюме
def analyze_resume(text):
    score = 0
    matched_skills = []

    for skill in job_card["skills"]:
        if skill.lower() in text.lower():
            matched_skills.append(skill)
            score += 20  # +20 баллов за каждый найденный навык

    experience_match = fuzz.partial_ratio(job_card["experience"], text)
    if experience_match > 70:
        score += 20

    return f"✅ Совпадение: {score}%\n🎯 Найденные навыки: {', '.join(matched_skills)}"

# Функция сравнения резюме
def compare_resumes(resumes):
    candidates = []

    for name, text in resumes:
        score = 0
        matched_skills = []

        for skill in job_card["skills"]:
            if skill.lower() in text.lower():
                matched_skills.append(skill)
                score += 20

        experience_match = fuzz.partial_ratio(job_card["experience"], text)
        if experience_match > 70:
            score += 20

        candidates.append((name, score, matched_skills))

    # Сортируем кандидатов по рейтингу
    candidates.sort(key=lambda x: x[1], reverse=True)

    # Формируем сравнительное заключение
    result = "📊 Рейтинг кандидатов:\n\n"
    for i, (name, score, skills) in enumerate(candidates, start=1):
        result += f"{i}. {name} — {score}% соответствия\n"
        result += f"   🎯 Навыки: {', '.join(skills) if skills else 'Нет совпадений'}\n\n"

    return result
