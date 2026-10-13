from dataset_common import fetch_candidate_questions, make_question, save_dataset


URLS = ["https://www.indiabix.com/hr-interview/questions-and-answers/"]

SEED = [
    ("Introduction", "Tell me about yourself and connect your background to the role.", "Keep it concise and role-focused.", ["Brief background", "Relevant skills", "Career direction"]),
    ("Motivation", "Why do you want to work for this company and this role?", "Show research and specific motivation.", ["Company research", "Role alignment", "Growth motivation"]),
    ("Strengths", "What is your strongest professional strength and where have you demonstrated it?", "Use evidence, not only adjectives.", ["Strength", "Example", "Outcome"]),
    ("Weakness", "Tell me about one area you are actively improving.", "Be honest and show a corrective action.", ["Real weakness", "Improvement plan", "Progress evidence"]),
    ("Career Goals", "Where do you see yourself in the next two to three years?", "Connect ambition with learning and contribution.", ["Clear goal", "Role fit", "Learning plan"]),
    ("Adaptability", "Describe a situation where you had to learn something quickly.", "Use a concrete example.", ["Context", "Learning method", "Result"]),
    ("Ownership", "Tell me about a time you took ownership without being asked.", "Show initiative and impact.", ["Problem", "Action", "Impact"]),
    ("Feedback", "How do you respond when you receive critical feedback?", "Show maturity and action.", ["Listening", "Reflection", "Improvement"]),
    ("Pressure", "How do you manage deadlines when multiple tasks compete for attention?", "Explain prioritization.", ["Prioritization", "Communication", "Delivery"]),
    ("Culture Fit", "What type of team environment helps you do your best work?", "Balance preferences with adaptability.", ["Team preference", "Collaboration style", "Adaptability"]),
    ("Decision Making", "Describe a decision you made with incomplete information.", "Show structured judgment.", ["Available data", "Decision logic", "Risk handling"]),
    ("Closing", "Why should we select you over other candidates?", "Summarize fit with evidence.", ["Role fit", "Proof points", "Confidence"]),
]


def main() -> None:
    live = fetch_candidate_questions(URLS, "HR", "HR")
    questions = [
        make_question("hr", index, "HR", topic, question, hint, points)
        for index, (topic, question, hint, points) in enumerate(SEED, start=1)
    ]
    offset = len(questions)
    for index, question in enumerate(live[:20], start=offset + 1):
        questions.append(make_question("hr", index, "HR", "HR", question, "Answer with a structured, specific example.", ["Direct answer", "Specific example", "Role relevance"], source="Live HTML extraction"))
    save_dataset("hr", questions)


if __name__ == "__main__":
    main()
