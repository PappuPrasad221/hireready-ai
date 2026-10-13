from dataset_common import fetch_candidate_questions, make_question, save_dataset


URLS = ["https://www.indiabix.com/hr-interview/questions-and-answers/"]

SEED = [
    ("Teamwork", "Tell me about a time you helped a teammate succeed.", "Use STAR and focus on contribution.", ["Situation", "Action", "Result"]),
    ("Conflict", "Describe a disagreement in a project and how you resolved it.", "Show communication maturity.", ["Conflict", "Conversation", "Resolution"]),
    ("Leadership", "Tell me about a time you led without having formal authority.", "Show influence.", ["Context", "Influence", "Outcome"]),
    ("Problem Solving", "Describe a complex problem you broke into smaller parts.", "Show method.", ["Problem", "Breakdown", "Result"]),
    ("Failure", "Tell me about a mistake you made and what changed afterward.", "Own the mistake.", ["Mistake", "Learning", "Preventive action"]),
    ("Pressure", "Give an example of handling pressure during a deadline.", "Show priorities and communication.", ["Deadline", "Prioritization", "Outcome"]),
    ("Ambiguity", "Tell me about a task where requirements were unclear.", "Show clarification and execution.", ["Ambiguity", "Clarifying questions", "Delivery"]),
    ("Communication", "Describe a time you explained a technical topic to a non-technical person.", "Show audience adaptation.", ["Audience", "Simplification", "Understanding"]),
    ("Initiative", "Tell me about a time you improved a process or workflow.", "Show measurable impact.", ["Before state", "Improvement", "Impact"]),
    ("Learning", "Describe a recent skill you learned and how you applied it.", "Connect learning to usage.", ["Skill", "Practice method", "Application"]),
    ("Ethics", "What would you do if asked to ignore a serious bug before a demo?", "Show judgment and escalation.", ["Risk", "Communication", "Responsible action"]),
    ("Customer Focus", "Tell me about a time you changed work based on user feedback.", "Show listening and iteration.", ["Feedback", "Change", "User impact"]),
]


def main() -> None:
    live = fetch_candidate_questions(URLS, "Behavioral", "Behavioral")
    questions = [
        make_question("behavioral", index, "Behavioral", topic, question, hint, points)
        for index, (topic, question, hint, points) in enumerate(SEED, start=1)
    ]
    offset = len(questions)
    for index, question in enumerate(live[:20], start=offset + 1):
        questions.append(make_question("behavioral", index, "Behavioral", "Behavioral", question, "Use the STAR structure.", ["Situation", "Task", "Action", "Result"], source="Live HTML extraction"))
    save_dataset("behavioral", questions)


if __name__ == "__main__":
    main()
