from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


# ----------------------------
# Question Bank (Demo: Algebra)
# ----------------------------
QUESTION_BANK = [
    {
        "id": 1,
        "concept": "Linear Equations",
        "question_type": "conceptual",
        "difficulty": "easy",
        "question": "If 2x + 3 = 11, what is the value of x?",
        "options": ["3", "4", "5", "6"],
        "correct": "4",
        "explanations": {
            "step_by_step": "We have 2x + 3 = 11. Subtract 3 from both sides → 2x = 8. Now divide both sides by 2 → x = 4.",
            "real_example": "Imagine you have 2 equal boxes of chocolates and 3 loose chocolates, total 11. Remove 3 loose ones → 8 left, equally in 2 boxes, so each box has 4 chocolates. That means x = 4.",
            "why_then_how": "Linear equations keep balance between two sides. To keep balance, whatever you do to one side, you must do to the other. Here we first remove +3 from both sides, then divide both sides by 2, giving x = 4."
        }
    },
    {
        "id": 2,
        "concept": "Linear Equations",
        "question_type": "numerical",
        "difficulty": "medium",
        "question": "Solve: 3x - 5 = 16",
        "options": ["5", "7", "9", "11"],
        "correct": "7",
        "explanations": {
            "step_by_step": "3x - 5 = 16. Add 5 on both sides → 3x = 21. Now divide both sides by 3 → x = 7.",
            "real_example": "Think of three equal baskets of apples minus 5 apples equals 16 apples. Add 5 back → 21 apples, divide into 3 baskets → 7 apples each, so x = 7.",
            "why_then_how": "We want x alone. First we reverse subtraction by adding 5, then reverse multiplication by dividing by 3, giving x = 7."
        }
    },
    {
        "id": 3,
        "concept": "Graph Interpretation",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question": "The graph of y = 2x + 1 cuts the y-axis at:",
        "options": ["(0, 1)", "(1, 0)", "(0, 2)", "(2, 0)"],
        "correct": "(0, 1)",
        "explanations": {
            "step_by_step": "On the y-axis, x = 0. Put x = 0 in y = 2x + 1 → y = 1. So the y-intercept is (0, 1).",
            "real_example": "Imagine you start at height 1 and for every step right you go 2 units up. Starting point on the y-axis is (0, 1).",
            "why_then_how": "The constant term in y = mx + c is the y-intercept. Here c = 1, so the graph crosses the y-axis at y = 1 → (0, 1)."
        }
    },
    {
        "id": 4,
        "concept": "Word Problems",
        "question_type": "conceptual",
        "difficulty": "medium",
        "question": "A number is doubled and then increased by 5 to get 19. What is the number?",
        "options": ["5", "6", "7", "8"],
        "correct": "7",
        "explanations": {
            "step_by_step": "Let the number be x. Doubling → 2x. Then increased by 5 → 2x + 5. Given 2x + 5 = 19. Subtract 5 → 2x = 14, divide by 2 → x = 7.",
            "real_example": "Think of a number, double it and add 5, you get 19. Try 7: double → 14, plus 5 → 19. So the number is 7.",
            "why_then_how": "We translate the story into an equation: 'doubled' → 2x, 'increased by 5' → +5, equal to 19. Then solve 2x + 5 = 19 step by step."
        }
    }
]


# ----------------------------
# Utility: Accuracy & Style
# ----------------------------
def compute_accuracy(logs, q_type=None):
    """Compute accuracy overall or for a specific question_type."""
    filtered = [l for l in logs if (q_type is None or l["question_type"] == q_type)]
    if not filtered:
        return 0.0
    correct = sum(1 for l in filtered if l["is_correct"])
    return correct / len(filtered)


def detect_learning_style(logs):
    """Very simple, interpretable learning-style classifier."""
    if not logs:
        return "Not enough data yet"

    avg_time = sum(l["time_taken_sec"] for l in logs) / len(logs)
    hint_rate = sum(1 for l in logs if l["used_hint"]) / len(logs)
    conceptual_acc = compute_accuracy(logs, "conceptual")
    numerical_acc = compute_accuracy(logs, "numerical")

    # Basic rules (you can tweak these)
    if avg_time > 30 and hint_rate > 0.4:
        return "Sequential + Slow-Paced + Example-Driven"
    if hint_rate > 0.4:
        return "Example-Driven Learner"
    if conceptual_acc < numerical_acc:
        return "Visual + Example-Driven Learner"
    if numerical_acc < conceptual_acc:
        return "Reasoning-First Learner"
    return "Balanced Learner"


def choose_explanation_style(style_label):
    """Map style label to explanation variant key."""
    if "Sequential" in style_label:
        return "step_by_step"
    if "Example" in style_label:
        return "real_example"
    if "Reasoning-First" in style_label:
        return "why_then_how"
    # default
    return "step_by_step"


# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Start a new session
        session["student_name"] = request.form.get("name") or "Learner"
        session["subject"] = request.form.get("subject") or "Algebra"
        session["current_index"] = 0
        session["logs"] = []
        return redirect(url_for("quiz"))
    return render_template("index.html")


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    logs = session.get("logs", [])

    last_style = detect_learning_style(logs)
    last_explanation = None
    last_question_text = None

    # Handle answer submission
    if request.method == "POST":
        q_id = int(request.form["question_id"])
        chosen = request.form.get("answer")
        time_taken = float(request.form.get("time_taken_sec", 0))
        used_hint = request.form.get("used_hint", "false") == "true"

        # find question
        question = next(q for q in QUESTION_BANK if q["id"] == q_id)
        is_correct = (chosen == question["correct"])

        # log interaction
        logs.append({
            "question_id": q_id,
            "question_type": question["question_type"],
            "difficulty": question["difficulty"],
            "time_taken_sec": time_taken,
            "used_hint": used_hint,
            "is_correct": is_correct
        })
        session["logs"] = logs

        # new style after this question
        last_style = detect_learning_style(logs)
        style_key = choose_explanation_style(last_style)
        last_explanation = question["explanations"][style_key]
        last_question_text = question["question"]

        # move to next question
        session["current_index"] = session.get("current_index", 0) + 1

    current_index = session.get("current_index", 0)

    if current_index >= len(QUESTION_BANK):
        return redirect(url_for("result"))

    current_question = QUESTION_BANK[current_index]

    return render_template(
        "quiz.html",
        question=current_question,
        last_style=last_style,
        last_explanation=last_explanation,
        last_question_text=last_question_text
    )


@app.route("/result")
def result():
    logs = session.get("logs", [])
    name = session.get("student_name", "Learner")

    total_questions = len(QUESTION_BANK)
    total_correct = sum(1 for l in logs if l["is_correct"])
    overall_acc = (total_correct / total_questions) * 100 if total_questions else 0

    avg_time = (
        sum(l["time_taken_sec"] for l in logs) / len(logs)
        if logs else 0
    )
    hint_rate = (
        sum(1 for l in logs if l["used_hint"]) / len(logs)
        if logs else 0
    )

    final_style = detect_learning_style(logs)

    return render_template(
        "result.html",
        name=name,
        total_questions=total_questions,
        total_correct=total_correct,
        overall_acc=overall_acc,
        avg_time=avg_time,
        hint_rate=hint_rate * 100,
        final_style=final_style,
        logs=logs
    )


if __name__ == "__main__":
    app.run(debug=True)
