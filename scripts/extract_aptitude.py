from dataset_common import fetch_candidate_questions, make_question, save_dataset


URLS = [
    "https://www.indiabix.com/aptitude/questions-and-answers/",
    "https://www.indiabix.com/logical-reasoning/questions-and-answers/",
]

SEED = [
    ("Percentages", "A candidate improves a test score from 60 to 75. What is the percentage increase?", "Use change divided by original.", ["Difference", "Base value", "Percentage"]),
    ("Time and Work", "If 4 people finish a task in 12 days, how many days will 6 people take at the same rate?", "Use inverse proportionality.", ["Work rate", "Inverse relation", "Calculation"]),
    ("Profit and Loss", "A product bought for 800 is sold at 920. Find the profit percentage.", "Profit divided by cost price.", ["Profit amount", "Cost base", "Percentage"]),
    ("Ratio", "Divide 900 in the ratio 2:3:4.", "Use sum of ratio parts.", ["Ratio sum", "Unit value", "Shares"]),
    ("Probability", "What is the probability of getting an even number on one fair die roll?", "Count favorable outcomes.", ["Sample space", "Favorable cases", "Probability"]),
    ("Average", "The average of five numbers is 24. If one number is 40, what is the average of the remaining four?", "Use total sum.", ["Total sum", "Subtract known value", "New average"]),
    ("Simple Interest", "Find simple interest on 5000 at 8 percent per year for 2 years.", "Use PRT/100.", ["Principal", "Rate", "Time"]),
    ("Speed", "A train travels 180 km in 3 hours. What is its average speed?", "Distance divided by time.", ["Distance", "Time", "Speed"]),
    ("Logical Reasoning", "If all developers are problem solvers and some problem solvers are designers, what can be concluded?", "Avoid unsupported conclusions.", ["Set relation", "Valid inference", "Limitations"]),
    ("Data Interpretation", "If interview pass rates are 40%, 50%, and 60% across three batches of equal size, what is the average pass rate?", "Equal-size average.", ["Equal weights", "Average", "Interpretation"]),
]


def main() -> None:
    live = fetch_candidate_questions(URLS, "Aptitude", "Aptitude")
    questions = [
        make_question("aptitude", index, "Aptitude", topic, question, hint, points, difficulty="easy")
        for index, (topic, question, hint, points) in enumerate(SEED, start=1)
    ]
    offset = len(questions)
    for index, question in enumerate(live[:25], start=offset + 1):
        questions.append(make_question("aptitude", index, "Aptitude", "Aptitude", question, "Solve step by step.", ["Formula", "Calculation", "Final answer"], source="Live HTML extraction"))
    save_dataset("aptitude", questions)


if __name__ == "__main__":
    main()
