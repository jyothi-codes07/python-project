import tkinter as tk
from tkinter import messagebox, ttk
import json
from datetime import datetime

# -------------------- Load Questions --------------------
try:
    with open("questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messagebox.showerror("Error", "Unable to load questions file!")
    exit()

# -------------------- Colors & Fonts --------------------
BG_COLOR = "#F0F8FF"          # Soft AliceBlue
QUESTION_TEXT = "Black"
OPTION_TEXT = "#2C3E50"
BTN_COLOR = "#1A5276"         # Deep blue
BTN_HOVER = "#5499C7"         # Soft blue hover
BTN_TEXT = "#FFFFFF"
EXPL_CORRECT = "dark green"
EXPL_WRONG = "#BF092F"

FONT_TITLE = ("Calibri", 28)
FONT_SUBTITLE = ("Verdana", 24)
FONT_QUEST = ("Verdana", 16)
FONT_BTN = ("Verdana", 13, "bold")  # ↓ smaller font size for buttons
FONT_EXPL = ("Verdana", 12, "italic")  # smaller font for explanation

SCORE_FILE = "scores.json"

# -------------------- Save Score --------------------
def save_score(name, score, total):
    percentage = (score / total) * 100
    entry = {
        "name": name,
        "score": score,
        "total": total,
        "percentage": round(percentage, 2)
    }
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    data.append(entry)
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# -------------------- Leaderboard Window --------------------
class LeaderboardWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Leaderboard")
        self.geometry("500x400")
        self.config(bg=BG_COLOR)

        tk.Label(self, text="🏆 Leaderboard 🏆", font=FONT_TITLE, bg=BG_COLOR, fg="#1A5276").pack(pady=20)

        try:
            with open(SCORE_FILE, "r", encoding="utf-8") as f:
                scores = json.load(f)
        except:
            scores = []

        if not scores:
            tk.Label(self, text="No scores recorded yet.", font=FONT_QUEST, bg=BG_COLOR).pack(pady=20)
            return

        scores.sort(key=lambda x: x["percentage"], reverse=True)

        tree = ttk.Treeview(self, columns=("name", "score", "percent"), show="headings", height=10)
        tree.heading("name", text="Player")
        tree.heading("score", text="Score")
        tree.heading("percent", text="Percentage")
        tree.column("name", width=150, anchor="center")
        tree.column("score", width=100, anchor="center")
        tree.column("percent", width=100, anchor="center")

        for s in scores[:10]:
            tree.insert("", "end", values=(s["name"], f"{s['score']}/{s['total']}", f"{s['percentage']}%"))

        tree.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Button(self, text="Close", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                  activebackground=BTN_HOVER, padx=15, pady=8, command=self.destroy).pack(pady=10)

# -------------------- Main Window --------------------
class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Famous Countries and Landmarks Quiz")
        self.geometry("750x550")
        self.config(bg=BG_COLOR)

        tk.Label(self, text="Welcome to", font=FONT_SUBTITLE, bg=BG_COLOR, fg="#2C3E50").pack(pady=(40, 5))
        tk.Label(self, text="Famous Countries and Landmarks Quiz", font=FONT_TITLE, bg=BG_COLOR, fg="#1ABC9C").pack(pady=(0, 20))
        tk.Label(self,
                 text="Test your knowledge of countries, famous landmarks, and historical facts from around the world.\nCan you get them all right?",
                 font=("Verdana", 14), bg=BG_COLOR, fg="#34495E", wraplength=650, justify="center").pack(pady=(0, 40))

        tk.Label(self, text="Enter your name:", font=("Verdana", 14), bg=BG_COLOR, fg="#2C3E50").pack(pady=(10, 5))
        self.name_entry = tk.Entry(self, font=("Verdana", 14), width=25, justify="center")
        self.name_entry.pack(pady=(0, 30))

        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=20)

        # Start Quiz button
        tk.Button(btn_frame, text="Start Quiz", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                  activebackground=BTN_HOVER, padx=30, pady=15, command=self.start_quiz).pack(side="left", padx=15)

        # View Leaderboard button
        tk.Button(btn_frame, text="View Leaderboard", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                  activebackground=BTN_HOVER, padx=25, pady=15, command=self.show_leaderboard).pack(side="left", padx=15)

    def start_quiz(self):
        player_name = self.name_entry.get().strip()
        if not player_name:
            messagebox.showwarning("Name Required", "Please enter your name before starting the quiz.")
            return
        self.destroy()
        QuizApp(questions, player_name)

    def show_leaderboard(self):
        LeaderboardWindow(self)

# -------------------- Quiz Window --------------------
class QuizApp(tk.Tk):
    def __init__(self, questions, player_name):
        super().__init__()
        self.title("Famous Countries and Landmarks Quiz")
        self.geometry("850x650")
        self.config(bg=BG_COLOR)

        self.questions = questions
        self.total = len(questions)
        self.current = 0
        self.user_answers = [None] * self.total
        self.locked_questions = [False] * self.total
        self.player_name = player_name

        # Timer
        self.time_left = 5 * 60
        top_frame = tk.Frame(self, bg=BG_COLOR)
        top_frame.pack(fill="x", pady=10, padx=20)

        self.player_label = tk.Label(top_frame, text=f"Player: {self.player_name}", font=FONT_QUEST, bg=BG_COLOR, fg="#1A5276")
        self.player_label.pack(side="left")

        self.timer_label = tk.Label(top_frame, text="", font=FONT_QUEST, bg=BG_COLOR, fg="#D35400")
        self.timer_label.pack(side="right")
        self.update_timer()

        # Question
        self.q_label = tk.Label(self, text="", font=FONT_QUEST, bg=BG_COLOR, fg=QUESTION_TEXT, wraplength=750, justify="left")
        self.q_label.pack(pady=(40, 15), anchor="w", padx=20)

        # Options
        self.selected = tk.IntVar(value=-1)
        self.radio_buttons = []
        for i in range(4):
            rb = tk.Radiobutton(self, text="", variable=self.selected, value=i,
                                font=FONT_QUEST, bg=BG_COLOR, fg=OPTION_TEXT,
                                selectcolor=BG_COLOR, activebackground=BG_COLOR,
                                anchor="w", justify="left", padx=10, pady=10,
                                command=self.show_explanation)
            rb.pack(anchor="w", fill="x", pady=5, ipadx=10, ipady=5, padx=20)
            self.radio_buttons.append(rb)

        # Explanation
        self.explanation_label = tk.Label(self, text="", font=FONT_EXPL, bg=BG_COLOR, wraplength=750, justify="left")
        self.explanation_label.pack(pady=15, anchor="w", padx=20)

        # Navigation
        nav = tk.Frame(self, bg=BG_COLOR, pady=20)
        nav.pack(fill="x")

        self.prev_btn = tk.Button(nav, text="◀ Previous", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                                  activebackground=BTN_HOVER, padx=25, pady=10, command=self.prev_question)
        self.prev_btn.pack(side="left", padx=10)

        self.next_btn = tk.Button(nav, text="Next ▶", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                                  activebackground=BTN_HOVER, padx=25, pady=10, command=self.next_question)
        self.next_btn.pack(side="left", padx=10)

        self.submit_btn = tk.Button(nav, text="Submit", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                                    activebackground=BTN_HOVER, padx=25, pady=10, command=self.show_result)
        self.submit_btn.pack(side="right", padx=10)

        self.progress_label = tk.Label(nav, text="", bg=BG_COLOR, font=FONT_BTN, fg=QUESTION_TEXT)
        self.progress_label.pack(side="right", padx=10)

        self.show_question()
        self.mainloop()

    # Timer
    def update_timer(self):
        if not hasattr(self, "timer_label") or not self.timer_label.winfo_exists():
            return
        minutes, seconds = divmod(self.time_left, 60)
        self.timer_label.config(text=f"Time Left: {minutes:02d}:{seconds:02d}")
        if self.time_left > 0:
            self.time_left -= 1
            self.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's Up!", "Time is over. The quiz will be submitted automatically.")
            self.show_result()

    # Show Question
    def show_question(self):
        q = self.questions[self.current]
        self.q_label.config(text=f"Q{self.current+1}. {q['question']}")
        opts = q.get("options", [])
        for i, rb in enumerate(self.radio_buttons):
            if i < len(opts):
                rb.config(text=opts[i], state="normal")
                rb.pack(anchor="w", fill="x", pady=5, ipadx=10, ipady=5, padx=20)
            else:
                rb.pack_forget()

        ua = self.user_answers[self.current]
        self.selected.set(ua if ua is not None else -1)
        self.explanation_label.config(text="", font=FONT_EXPL)

        if self.locked_questions[self.current]:
            for rb in self.radio_buttons:
                rb.config(state="disabled")
            correct_idx = q["answer"]
            if ua == correct_idx:
                self.explanation_label.config(text=f"Correct! ✅\n{q.get('explanation','')}", fg=EXPL_CORRECT)
            elif ua is not None:
                self.explanation_label.config(text=f"Wrong ❌\nCorrect answer: {q['options'][correct_idx]}\n{q.get('explanation','')}", fg=EXPL_WRONG)

        self.prev_btn.config(state="normal" if self.current > 0 else "disabled")
        self.next_btn.config(state="normal" if self.current < self.total-1 else "disabled")
        self.progress_label.config(text=f"{self.current+1}/{self.total}")

    # Save Answer
    def save_answer(self):
        val = self.selected.get()
        self.user_answers[self.current] = val if val >= 0 else None

    # Show Explanation
    def show_explanation(self):
        ua = self.selected.get()
        q = self.questions[self.current]
        correct_idx = q["answer"]
        explanation = q.get("explanation", "")
        if ua >= 0 and not self.locked_questions[self.current]:
            self.save_answer()
            if ua == correct_idx:
                self.explanation_label.config(text=f"Correct! ✅\n{explanation}", fg=EXPL_CORRECT, font=FONT_EXPL)
            else:
                self.explanation_label.config(text=f"Wrong ❌\nCorrect answer: {q['options'][correct_idx]}\n{explanation}", fg=EXPL_WRONG, font=FONT_EXPL)
            self.locked_questions[self.current] = True
            for rb in self.radio_buttons:
                rb.config(state="disabled")

    # Navigation
    def next_question(self):
        if self.current < self.total - 1:
            self.current += 1
            self.show_question()

    def prev_question(self):
        if self.current > 0:
            self.current -= 1
            self.show_question()

    # Show Result
    def show_result(self):
        self.save_answer()
        unanswered = [i+1 for i, ans in enumerate(self.user_answers) if ans is None]
        if unanswered:
            proceed = messagebox.askyesno(
                "⚠️ Unanswered Questions",
                f"You haven't answered question(s): {', '.join(map(str, unanswered))}.\n\nDo you want to submit anyway?"
            )
            if not proceed:
                return

        score = sum(1 for idx, q in enumerate(self.questions) if self.user_answers[idx] == q["answer"])
        save_score(self.player_name, score, self.total)
        percentage = (score / self.total) * 100

        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text=f"Quiz Completed, {self.player_name}!", font=FONT_TITLE, bg=BG_COLOR, fg=QUESTION_TEXT).pack(pady=50)
        tk.Label(self, text=f"Score: {score} / {self.total}", font=FONT_QUEST, bg=BG_COLOR, fg=QUESTION_TEXT).pack(pady=10)
        tk.Label(self, text=f"Percentage: {percentage:.2f}%", font=FONT_QUEST, bg=BG_COLOR, fg=QUESTION_TEXT).pack(pady=10)

        if score == self.total:
            msg = "🎉 Perfect Score! Congratulations! 🎉"
        elif percentage >= 75:
            msg = "🎉 Well Done! 🎉"
        else:
            msg = "Keep Practicing! 👍"

        tk.Label(self, text=msg, font=FONT_QUEST, bg=BG_COLOR, fg="#3B9797").pack(pady=20)

        # Show leaderboard
        LeaderboardWindow(self)

        # Restart / Exit buttons
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=15)
        tk.Button(btn_frame, text="Play Again", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                  activebackground=BTN_HOVER, padx=40, pady=12, command=self.restart).pack(side="left", padx=20)
        tk.Button(btn_frame, text="Exit", font=FONT_BTN, bg=BTN_COLOR, fg=BTN_TEXT,
                  activebackground=BTN_HOVER, padx=40, pady=12, command=self.destroy).pack(side="left", padx=20)

    def restart(self):
        self.destroy()
        MainWindow().mainloop()

# -------------------- Run App --------------------
MainWindow().mainloop()






