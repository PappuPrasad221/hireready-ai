from dataset_common import fetch_candidate_questions, make_question, save_dataset


URLS = [
    "https://www.indiabix.com/technical/interview-questions-and-answers/",
    "https://www.indiabix.com/computer-science/questions-and-answers/",
]

SEED = [
    ("OOP", "Explain encapsulation, inheritance, polymorphism, and abstraction with one practical example.", "Cover definitions and usage.", ["Four OOP pillars", "Example", "Trade-offs"]),
    ("DBMS", "How would you design tables for a student interview platform and avoid duplicate data?", "Discuss normalization and keys.", ["Entities", "Relationships", "Normalization"]),
    ("SQL", "What is the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN?", "Explain with use cases.", ["Join behavior", "Null handling", "Example"]),
    ("API", "Design a REST API endpoint for submitting an interview answer.", "Include request, validation, and response.", ["Endpoint design", "Validation", "Error handling"]),
    ("React", "How do React state, props, and effects work together in an interview room UI?", "Connect concepts to UI behavior.", ["State", "Props", "Effects"]),
    ("Python", "How would you handle exceptions and logging in a FastAPI service?", "Explain reliability.", ["Try/except", "HTTP errors", "Structured logs"]),
    ("FastAPI", "What happens when a FastAPI request reaches a route handler?", "Explain the lifecycle.", ["Routing", "Validation", "Response model"]),
    ("Firebase", "How would you structure Firestore collections for users, interviews, evaluations, and reports?", "Discuss document design.", ["Collections", "Relationships", "Query needs"]),
    ("Machine Learning", "How do you prevent overfitting in a machine learning model?", "Mention validation and regularization.", ["Train/test split", "Regularization", "Evaluation metrics"]),
    ("System Design", "Design a scalable AI interview platform that records video and sends reports by email.", "Think through components.", ["Frontend", "Backend", "Storage", "Email workflow"]),
    ("Security", "What security risks exist when uploading resumes and generating reports?", "Mention validation and secrets.", ["File validation", "Secret handling", "Access control"]),
    ("Testing", "How would you test a resume upload API and an interview evaluation API?", "Cover unit and integration tests.", ["Test cases", "Mocking", "Assertions"]),
    ("Performance", "How would you reduce latency in an AI-powered interview question generation flow?", "Discuss caching and async work.", ["Caching", "Async processing", "Timeout handling"]),
    ("Architecture", "When would you choose SQL over Firestore for an analytics-heavy product?", "Compare data models.", ["Relational needs", "Query patterns", "Consistency"]),
    ("Debugging", "A production API returns the same job insights for every company. How would you debug it?", "Trace inputs and external calls.", ["Input tracing", "Cache check", "API response validation"]),
]


def main() -> None:
    live = fetch_candidate_questions(URLS, "Technical", "Technical")
    questions = [
        make_question("technical", index, "Technical", topic, question, hint, points)
        for index, (topic, question, hint, points) in enumerate(SEED, start=1)
    ]
    offset = len(questions)
    for index, question in enumerate(live[:25], start=offset + 1):
        questions.append(make_question("technical", index, "Technical", "Technical", question, "Explain clearly with a practical example.", ["Correct concept", "Example", "Trade-off"], source="Live HTML extraction"))
    save_dataset("technical", questions)


if __name__ == "__main__":
    main()
