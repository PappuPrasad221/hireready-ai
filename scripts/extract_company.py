from dataset_common import fetch_candidate_questions, make_question, save_dataset


URLS = ["https://www.indiabix.com/placement-papers/companies/"]

SEED = [
    ("TCS", "TCS", "How would you prepare for a service-based company interview where communication and fundamentals are both tested?", "Balance HR and basics.", ["Company context", "Fundamentals", "Communication"]),
    ("Infosys", "Infosys", "Explain how your project experience maps to a large enterprise software environment.", "Connect project scale to enterprise needs.", ["Project relevance", "Team process", "Quality"]),
    ("Wipro", "Wipro", "How would you handle being assigned to a technology stack that is new to you?", "Show adaptability.", ["Learning plan", "Mentorship", "Delivery"]),
    ("Accenture", "Accenture", "Describe how you would work with clients when requirements keep changing.", "Show consulting mindset.", ["Requirement tracking", "Communication", "Change handling"]),
    ("Cognizant", "Cognizant", "What makes you ready for a role involving both technical delivery and business communication?", "Show dual ability.", ["Technical foundation", "Communication", "Business awareness"]),
    ("Capgemini", "Capgemini", "Tell me how you would explain project risks to a manager before a release.", "Show risk communication.", ["Risk identification", "Impact", "Mitigation"]),
    ("Amazon", "Amazon", "Describe a time you showed ownership when the expected outcome was uncertain.", "Use ownership principle.", ["Ownership", "Bias for action", "Result"]),
    ("Microsoft", "Microsoft", "How would you design a feature with accessibility and reliability in mind?", "Show inclusive engineering.", ["Accessibility", "Reliability", "Testing"]),
    ("Google", "Google", "How do you approach solving an unfamiliar technical problem during an interview?", "Show structured problem solving.", ["Clarification", "Approach", "Complexity"]),
    ("Deloitte", "Deloitte", "How would you present technical findings to a non-technical stakeholder?", "Show consulting communication.", ["Audience", "Summary", "Recommendation"]),
    ("IBM", "IBM", "What is your approach to learning cloud or AI tools for an enterprise project?", "Show structured learning.", ["Learning path", "Hands-on practice", "Governance"]),
    ("HCL", "HCL", "How would you debug an application issue reported by a customer?", "Show support workflow.", ["Reproduce", "Logs", "Root cause"]),
]


def main() -> None:
    live = fetch_candidate_questions(URLS, "Company", "Placement")
    questions = [
        make_question("company", index, "Company", topic, question, hint, points, company=company)
        for index, (company, topic, question, hint, points) in enumerate(SEED, start=1)
    ]
    offset = len(questions)
    for index, question in enumerate(live[:25], start=offset + 1):
        questions.append(make_question("company", index, "Company", "Placement", question, "Answer with company-specific context.", ["Company fit", "Role fit", "Example"], source="Live HTML extraction"))
    save_dataset("company", questions)


if __name__ == "__main__":
    main()
