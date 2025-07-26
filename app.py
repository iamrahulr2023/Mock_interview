
import streamlit as st
import requests
import time
import re
import os
import json
from dotenv import load_dotenv

load_dotenv()

# ---------- API Keys ----------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
JDoodle_CLIENT_ID = os.getenv("JDoodle_CLIENT_ID")
JDoodle_CLIENT_SECRET = os.getenv("JDoodle_CLIENT_SECRET")

# ---------- Generate MCQs from Groq ----------
def generate_mcqs(job_desc):
    prompt = f"""Generate 5 technical multiple-choice questions (MCQs) with 4 options (A to D) and provide the correct answer for each.
Job Description: {job_desc}
Format:
Q1. ...
A. ...
B. ...
C. ...
D. ...
Answer: B
Q2. ...
..."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        st.error(f"Error generating MCQs: {e}")
        return ""

# ---------- Generate Coding Question ----------
def generate_coding_question(job_desc):
    prompt = f"""Generate 1 Python coding question suitable for a technical interview based on the following job description: {job_desc}.
Include:
- Problem description
- Input format
- Output format
- 2 sample test cases in this format:
Input:
<example input>
Output:
<expected output>
"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        st.error(f"Error generating coding question: {e}")
        return ""

# ---------- Run Python Code using JDoodle ----------
def run_code(code, stdin=""):
    url = "https://api.jdoodle.com/v1/execute"
    data = {
        "clientId": JDoodle_CLIENT_ID,
        "clientSecret": JDoodle_CLIENT_SECRET,
        "script": code,
        "language": "python3",
        "versionIndex": "4",
        "stdin": stdin
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("output", "❌ Execution Failed or No Output")
    except requests.RequestException as e:
        st.error(f"Error executing code: {e}")
        return "❌ Execution Failed"

# ---------- Parse MCQs ----------
def parse_mcqs(raw_text):
    questions = []
    blocks = re.split(r'Q\d+\.', raw_text)
    for block in blocks[1:]:
        lines = block.strip().split('\n')
        if len(lines) < 6:
            continue
        q_text = lines[0].strip()
        options = [line.strip() for line in lines[1:5] if re.match(r'^[A-D]\.', line)]
        answer_line = next((line for line in lines if line.lower().startswith("answer:")), None)
        if answer_line and len(options) == 4:
            correct = answer_line.split(":")[1].strip().upper()
            questions.append({
                "question": q_text,
                "options": options,
                "answer": correct
            })
    return questions

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Mock Interview", layout="wide")
st.title("💼 AI-Powered Mock Interview Platform")

if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.score = 0
    st.session_state.timer_start = None
    st.session_state.mcqs = []
    st.session_state.user_answers = []
    st.session_state.code_question = ""
    st.session_state.test_cases = []

# ---------- Job Description Input ----------
job_desc = st.text_area("📄 Enter Job Description:", height=100)

if st.button("🎯 Generate Mock Interview") and job_desc:
    with st.spinner("Generating MCQs and coding question..."):
        mcqs_raw = generate_mcqs(job_desc)
        st.session_state.mcqs = parse_mcqs(mcqs_raw)
        st.session_state.user_answers = [None] * len(st.session_state.mcqs)
        st.session_state.code_question = generate_coding_question(job_desc)
        # Extract test cases from coding question
        test_cases = []
        test_blocks = re.findall(r'Input:\n(.*?)\nOutput:\n(.*?)(?=\n\n|$)', st.session_state.code_question, re.DOTALL)
        for inp, out in test_blocks:
            test_cases.append({"input": inp.strip(), "output": out.strip()})
        st.session_state.test_cases = test_cases
        st.session_state.step = 1
        st.rerun()

# ---------- MCQ Round ----------
if st.session_state.step == 1:
    st.header("🧠 MCQ Round")
    if not st.session_state.mcqs:
        st.error("No MCQs generated. Please try again.")
    else:
        for idx, q in enumerate(st.session_state.mcqs):
            st.subheader(f"Q{idx+1}. {q['question']}")
            st.session_state.user_answers[idx] = st.radio(
                "Choose your answer:",
                options=q["options"],
                key=f"q_{idx}",
                index=None
            )

        if st.button("✅ Submit MCQ Answers"):
            if None in st.session_state.user_answers:
                st.warning("Please answer all questions before submitting.")
            else:
                correct = 0
                for idx, q in enumerate(st.session_state.mcqs):
                    selected = st.session_state.user_answers[idx]
                    if selected and selected.startswith(f"{q['answer']}."):
                        correct += 1
                st.session_state.score += correct * 10
                st.success(f"✅ You got {correct} out of {len(st.session_state.mcqs)} correct! Score: {correct * 10}")
                st.session_state.step = 2
                st.rerun()

# ---------- Coding Round ----------
if st.session_state.step == 2:
    st.header("💻 Coding Round")
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("### 📘 Question")
        st.markdown(st.session_state.code_question)

    with col2:
        st.markdown("### ✍️ Code Editor")
        code_input = st.text_area("Write your Python code here:", height=250, key="code_area")

        st.markdown("### 🧪 Test Cases")
        test_inputs = st.text_area(
            "Input Cases",
            value="\n".join([tc["input"] for tc in st.session_state.test_cases]),
            height=100
        )
        expected_outputs = st.text_area(
            "Expected Outputs",
            value="\n".join([tc["output"] for tc in st.session_state.test_cases]),
            height=100
        )

        if st.session_state.timer_start is None:
            if st.button("⏳ Start Coding Timer"):
                st.session_state.timer_start = time.time()
                st.rerun()
        else:
            elapsed = int(time.time() - st.session_state.timer_start)
            remaining = max(0, 300 - elapsed)
            st.info(f"⏳ Time Remaining: {remaining // 60}:{remaining % 60:02d}")

        col_run, col_submit, col_end = st.columns([1, 1, 1])
        run_clicked = col_run.button("🧪 Run Code")
        submit_clicked = col_submit.button("✅ Submit Code")
        end_clicked = col_end.button("🚪 End Test")

        if run_clicked and code_input:
            st.markdown("### 🔍 Output Comparison")
            inputs = test_inputs.strip().splitlines()
            expected = expected_outputs.strip().splitlines()
            for i, (inp, exp) in enumerate(zip(inputs, expected)):
                result = run_code(code_input, inp).strip()
                st.code(f"Test Case {i+1}:\nInput: {inp}\nExpected: {exp}\nYour Output: {result}")

        if submit_clicked and code_input:
            if remaining <= 0:
                st.warning("⏰ Time's up!")
            inputs = test_inputs.strip().splitlines()
            expected = expected_outputs.strip().splitlines()
            if len(inputs) != len(expected):
                st.error("Number of inputs and expected outputs must match.")
            else:
                passed = 0
                for inp, exp in zip(inputs, expected):
                    result = run_code(code_input, inp).strip()
                    if result == exp.strip():
                        passed += 1
                score = 20 if passed == len(expected) else 0
                st.session_state.score += score
                if score > 0:
                    st.success(f"✅ All test cases passed! {score} points awarded.")
                else:
                    st.warning("❌ Some test cases failed. No points awarded.")
                st.session_state.step = 3
                st.rerun()

        if end_clicked:
            st.session_state.step = 3
            st.rerun()

# ---------- Final Result ----------
if st.session_state.step == 3:
    st.header("🎓 Interview Summary")
    st.success(f"🏆 Final Score: {st.session_state.score} / 50")
    if st.button("🔁 Restart"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()