import random
import re


# ============================================================
# QUESTION BANK
# ============================================================

QUESTION_BANK = {

    "Python": {
        "Easy": [
            "What is Python and why is it popular?",
            "What are variables in Python?",
            "What is the difference between a list and a tuple in Python?",
            "What are Python dictionaries?",
            "What is a function in Python?"
        ],

        "Medium": [
            "What is the difference between a list, tuple, set and dictionary in Python?",
            "Explain exception handling in Python with an example.",
            "What is the difference between == and is in Python?",
            "Explain Python list comprehension.",
            "What are modules and packages in Python?"
        ],

        "Hard": [
            "Explain object-oriented programming in Python with an example.",
            "What are decorators in Python and why are they useful?",
            "Explain generators and the yield keyword in Python.",
            "What is the difference between shallow copy and deep copy?",
            "Explain Python memory management and garbage collection."
        ]
    },

    "Java": {
        "Easy": [
            "What is Java and what are its main features?",
            "What is a class and an object in Java?",
            "What is inheritance in Java?",
            "What is a constructor in Java?",
            "What is the difference between JDK, JRE and JVM?"
        ],

        "Medium": [
            "Explain method overloading and method overriding in Java.",
            "What is encapsulation in Java?",
            "Explain polymorphism with an example.",
            "What is the difference between an interface and an abstract class?",
            "What is exception handling in Java?"
        ],

        "Hard": [
            "Explain the four pillars of OOP in Java.",
            "How does Java achieve platform independence?",
            "Explain the Java Collections Framework.",
            "What is multithreading in Java?",
            "Explain garbage collection in Java."
        ]
    },

    "Technical": {
        "Easy": [
            "What is an operating system?",
            "What is a database?",
            "What is a computer network?",
            "What is an IP address?",
            "What is the difference between hardware and software?"
        ],

        "Medium": [
            "What is the difference between SQL and NoSQL databases?",
            "Explain the difference between HTTP and HTTPS.",
            "What is normalization in a database?",
            "What is the difference between a process and a thread?",
            "Explain primary key and foreign key."
        ],

        "Hard": [
            "Explain the OSI model and its seven layers.",
            "Explain database indexing and its advantages.",
            "What is deadlock in an operating system?",
            "Explain TCP three-way handshake.",
            "What is database transaction management?"
        ]
    },

    "HR": {
        "Easy": [
            "Tell me about yourself.",
            "What are your strengths?",
            "What are your weaknesses?",
            "Why do you want to join our company?",
            "Where do you see yourself in five years?"
        ],

        "Medium": [
            "Why should we hire you?",
            "Tell me about a challenge you faced and how you solved it.",
            "How do you handle pressure?",
            "How do you work in a team?",
            "Why should we select you over other candidates?"
        ],

        "Hard": [
            "Tell me about a failure and what you learned from it.",
            "How would you handle a conflict with a teammate?",
            "What would you do if you disagreed with your manager?",
            "Describe a situation where you demonstrated leadership.",
            "How would you handle multiple deadlines at the same time?"
        ]
    },

    "Aptitude": {
        "Easy": [
            "If a number is increased by 20% and becomes 120, what was the original number?",
            "What is the average of 10, 20 and 30?",
            "If a product costs ₹500 and has a 10% discount, what is the selling price?",
            "What is 25% of 200?",
            "If a car travels 60 km in 2 hours, what is its average speed?"
        ],

        "Medium": [
            "A train travels 240 km in 4 hours. What is its average speed?",
            "A product is bought for ₹800 and sold for ₹960. What is the profit percentage?",
            "If 5 workers complete a task in 12 days, how many days will 10 workers take?",
            "What is the probability of getting a head when a fair coin is tossed?",
            "A number is increased by 25% and then decreased by 20%. What is the overall percentage change?"
        ],

        "Hard": [
            "A can complete a task in 12 days and B can complete it in 18 days. How long will they take together?",
            "A train 180 meters long crosses a pole in 9 seconds. Find its speed in km/h.",
            "If the ratio of two numbers is 3:5 and their sum is 64, find the numbers.",
            "A shopkeeper marks an item 40% above cost price and gives a 10% discount. Find the profit percentage.",
            "A sum becomes ₹12,100 in two years at 10% compound interest per annum. Find the principal."
        ]
    },

    "Resume": {
        "Easy": [
            "Tell me about yourself based on your resume.",
            "Which skill mentioned in your resume are you currently improving?",
            "Tell me about your most important project.",
            "What technologies have you worked with?",
            "What was your biggest learning from your projects?"
        ],

        "Medium": [
            "Explain one of the projects mentioned in your resume.",
            "What problem does your project solve?",
            "What challenges did you face while developing your project?",
            "Why did you choose the technologies used in your project?",
            "How would you improve your project in the future?"
        ],

        "Hard": [
            "Explain the architecture of your most important project.",
            "What technical problem in your project required the most debugging?",
            "If your project had to support 100,000 users, what changes would you make?",
            "How did you test your project?",
            "What would you change if you developed the project again?"
        ]
    }
}


# ============================================================
# IMPORTANT CONCEPTS FOR EVALUATION
# ============================================================

CONCEPT_KEYWORDS = {

    "python": [
        "python",
        "dynamic",
        "interpreted",
        "indentation",
        "list",
        "tuple",
        "dictionary",
        "set",
        "function",
        "exception",
        "class",
        "object",
        "decorator",
        "generator",
        "yield",
        "module"
    ],

    "java": [
        "java",
        "class",
        "object",
        "inheritance",
        "encapsulation",
        "polymorphism",
        "abstraction",
        "interface",
        "constructor",
        "method",
        "overloading",
        "overriding",
        "jvm",
        "jdk",
        "jre",
        "exception"
    ],

    "technical": [
        "database",
        "sql",
        "network",
        "operating system",
        "process",
        "thread",
        "server",
        "client",
        "http",
        "https",
        "tcp",
        "ip",
        "primary key",
        "foreign key",
        "normalization",
        "osi"
    ],

    "hr": [
        "communication",
        "team",
        "teamwork",
        "learning",
        "problem",
        "solution",
        "experience",
        "project",
        "skill",
        "goal",
        "career",
        "company",
        "responsibility",
        "challenge",
        "strength"
    ],

    "resume": [
        "project",
        "skill",
        "technology",
        "experience",
        "learning",
        "challenge",
        "solution",
        "resume",
        "development",
        "improvement"
    ],

    "aptitude": [
        "calculation",
        "formula",
        "percentage",
        "ratio",
        "average",
        "profit",
        "loss",
        "speed",
        "time",
        "distance",
        "probability",
        "interest"
    ]
}


# ============================================================
# QUESTION GENERATOR
# ============================================================

def generate_question(interview_type, difficulty):

    interview_type = interview_type or "Technical"
    difficulty = difficulty or "Medium"

    if interview_type not in QUESTION_BANK:
        interview_type = "Technical"

    if difficulty not in QUESTION_BANK[interview_type]:
        difficulty = "Medium"

    questions = QUESTION_BANK[interview_type][difficulty]

    if not questions:
        return "Tell me about your technical skills."

    return random.choice(questions)


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"[^a-zA-Z0-9\s+#.-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# WORD COUNT
# ============================================================

def get_word_count(text):

    if not text:
        return 0

    return len(
        clean_text(text).split()
    )


# ============================================================
# FIND KEYWORDS
# ============================================================

def find_keywords(interview_type, question, answer):

    question_text = clean_text(question)
    answer_text = clean_text(answer)

    combined_text = (
        question_text + " " + answer_text
    )

    category = (
        interview_type or "Technical"
    ).lower()

    keywords = CONCEPT_KEYWORDS.get(
        category,
        CONCEPT_KEYWORDS["technical"]
    )

    found = []

    for keyword in keywords:

        keyword_clean = clean_text(keyword)

        if keyword_clean in combined_text:

            if keyword_clean not in found:
                found.append(keyword_clean)

    return found


# ============================================================
# QUESTION-SPECIFIC KEYWORDS
# ============================================================

def question_keywords(question):

    question = clean_text(question)

    keyword_groups = {

        "inheritance": [
            "class",
            "parent",
            "child",
            "extends",
            "reuse",
            "inherit"
        ],

        "encapsulation": [
            "class",
            "data",
            "methods",
            "private",
            "public",
            "access"
        ],

        "polymorphism": [
            "same",
            "method",
            "overloading",
            "overriding",
            "compile",
            "runtime"
        ],

        "exception": [
            "try",
            "catch",
            "finally",
            "error",
            "exception",
            "handle"
        ],

        "list": [
            "ordered",
            "mutable",
            "element",
            "index"
        ],

        "tuple": [
            "ordered",
            "immutable",
            "element"
        ],

        "dictionary": [
            "key",
            "value",
            "mapping"
        ],

        "database": [
            "data",
            "table",
            "record",
            "query",
            "database"
        ],

        "primary key": [
            "unique",
            "identify",
            "record",
            "null"
        ],

        "foreign key": [
            "relationship",
            "table",
            "reference",
            "primary"
        ],

        "http": [
            "request",
            "response",
            "protocol",
            "web"
        ],

        "https": [
            "secure",
            "encryption",
            "ssl",
            "tls"
        ],

        "operating system": [
            "hardware",
            "software",
            "process",
            "memory",
            "resource"
        ],

        "team": [
            "communication",
            "collaboration",
            "teamwork",
            "support",
            "goal"
        ],

        "challenge": [
            "problem",
            "solution",
            "action",
            "result",
            "learning"
        ],

        "project": [
            "problem",
            "technology",
            "role",
            "implementation",
            "result"
        ]
    }

    expected = []

    for topic, words in keyword_groups.items():

        if topic in question:

            expected.extend(words)

    return list(dict.fromkeys(expected))


# ============================================================
# EVALUATION
# ============================================================

def evaluate_answer(
    interview_type,
    question,
    answer
):

    answer = answer or ""

    cleaned_answer = clean_text(answer)

    word_count = get_word_count(answer)

    found_keywords = find_keywords(
        interview_type,
        question,
        answer
    )

    expected_keywords = question_keywords(
        question
    )

    matched_expected = []

    for keyword in expected_keywords:

        if clean_text(keyword) in cleaned_answer:

            matched_expected.append(
                keyword
            )

    # --------------------------------------------------------
    # BASE SCORE
    # --------------------------------------------------------

    score = 4

    # Answer length
    if word_count >= 100:
        score += 2
    elif word_count >= 70:
        score += 1.5
    elif word_count >= 40:
        score += 1
    elif word_count >= 20:
        score += 0.5

    # General concept relevance
    if len(found_keywords) >= 5:
        score += 2
    elif len(found_keywords) >= 3:
        score += 1.5
    elif len(found_keywords) >= 1:
        score += 0.5

    # Question-specific relevance
    if len(matched_expected) >= 4:
        score += 1.5
    elif len(matched_expected) >= 2:
        score += 1
    elif len(matched_expected) >= 1:
        score += 0.5

    # --------------------------------------------------------
    # EMPTY / VERY SHORT ANSWER
    # --------------------------------------------------------

    if word_count == 0:

        score = 1

        evaluation = (
            "No answer was provided. "
            "Try to answer the question clearly "
            "and explain your reasoning."
        )

        return {
            "score": score,
            "evaluation": evaluation
        }

    if word_count < 8:

        score = min(score, 3)

        evaluation = (
            "Your answer is too short. "
            "Try to explain the concept with "
            "a definition, explanation, and example."
        )

        return {
            "score": score,
            "evaluation": evaluation
        }

    # --------------------------------------------------------
    # LIMIT SCORE
    # --------------------------------------------------------

    score = round(
        min(max(score, 1), 10)
    )

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    feedback = []

    if word_count < 20:

        feedback.append(
            "Try to provide a more detailed explanation."
        )

    elif word_count < 40:

        feedback.append(
            "Your answer has a reasonable start, "
            "but it could include more detail."
        )

    else:

        feedback.append(
            "Your answer has a good level of detail."
        )

    if len(found_keywords) == 0:

        feedback.append(
            "Try to include important technical "
            "concepts related to the question."
        )

    elif len(found_keywords) < 3:

        feedback.append(
            "Add more relevant technical concepts "
            "to make your answer stronger."
        )

    else:

        feedback.append(
            "You included several relevant concepts."
        )

    if expected_keywords:

        missing_keywords = [
            keyword
            for keyword in expected_keywords
            if clean_text(keyword)
            not in cleaned_answer
        ]

        if missing_keywords:

            missing_display = ", ".join(
                missing_keywords[:4]
            )

            feedback.append(
                "Consider discussing: "
                + missing_display
                + "."
            )

    # --------------------------------------------------------
    # INTERVIEW TYPE FEEDBACK
    # --------------------------------------------------------

    if interview_type == "HR":

        if (
            "example" not in cleaned_answer
            and "experience" not in cleaned_answer
        ):

            feedback.append(
                "For HR questions, include a short "
                "real example or experience when possible."
            )

    elif interview_type in [
        "Python",
        "Java",
        "Technical"
    ]:

        if "example" not in cleaned_answer:

            feedback.append(
                "Adding a practical example would "
                "make the technical answer stronger."
            )

    elif interview_type == "Resume":

        if "project" in question.lower():

            if "problem" not in cleaned_answer:

                feedback.append(
                    "Explain the problem your project "
                    "was designed to solve."
                )

            if "technology" not in cleaned_answer:

                feedback.append(
                    "Mention the technologies you used "
                    "and why you selected them."
                )

    # --------------------------------------------------------
    # SCORE-BASED SUMMARY
    # --------------------------------------------------------

    if score >= 9:

        summary = (
            "Excellent answer. "
            "Your response is relevant, detailed, "
            "and includes strong concepts."
        )

    elif score >= 8:

        summary = (
            "Very good answer. "
            "You explained the topic well with "
            "relevant information."
        )

    elif score >= 7:

        summary = (
            "Good answer. "
            "The main idea is clear, but you can "
            "add more technical depth."
        )

    elif score >= 5:

        summary = (
            "Average answer. "
            "You have the basic idea, but the "
            "explanation needs more clarity and detail."
        )

    else:

        summary = (
            "The answer needs improvement. "
            "Focus on understanding the concept "
            "and explaining it step by step."
        )

    # --------------------------------------------------------
    # FINAL EVALUATION
    # --------------------------------------------------------

    evaluation = (
        summary
        + "\n\n"
        + "\n".join(
            "• " + item
            for item in feedback
        )
    )

    return {
        "score": score,
        "evaluation": evaluation
    }


# ============================================================
# TEST FUNCTION
# ============================================================

if __name__ == "__main__":

    question = (
        "What is inheritance in Java?"
    )

    answer = (
        "Inheritance is an OOP concept in Java "
        "where a child class can inherit properties "
        "and methods from a parent class. "
        "It helps with code reuse. We use the "
        "extends keyword to create inheritance."
    )

    result = evaluate_answer(
        "Java",
        question,
        answer
    )

    print("Question:")
    print(question)

    print("\nAnswer:")
    print(answer)

    print("\nScore:")
    print(result["score"], "/ 10")

    print("\nEvaluation:")
    print(result["evaluation"])