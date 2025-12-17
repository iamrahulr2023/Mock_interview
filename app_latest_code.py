
# import streamlit as st
# import requests
# import time
# import re
# import os
# import json


# # from dotenv import load_dotenv

# # load_dotenv()

# # ---------- API Keys ----------

# from dotenv import load_dotenv
# load_dotenv()
# # GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# # JDoodle_CLIENT_ID = os.getenv("JDoodle_CLIENT_ID")
# # JDoodle_CLIENT_SECRET = os.getenv("JDoodle_CLIENT_SECRET")

# # ---------- API Keys ----------
# GROQ_API_KEY = "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"
# JDoodle_CLIENT_ID = "d3c56d56b7011b33205be169ebe24eaf"
# JDoodle_CLIENT_SECRET = "4a321690766787f5afbf1937b6acd531785833a39fbc932733592e83de6d15a8"


# # ---------- Generate MCQs from Groq ----------
# def generate_mcqs(job_desc):
#     prompt = f"""Generate 5 technical multiple-choice questions (MCQs) with 4 options (A to D) and provide the correct answer for each.
# Job Description: {job_desc}
# Format:
# Q1. ...
# A. ...
# B. ...
# C. ...
# D. ...
# Answer: B
# Q2. ...
# ..."""
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.7
#     }
#     try:
#         response = requests.post(url, headers=headers, json=body)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except requests.RequestException as e:
#         st.error(f"Error generating MCQs: {e}")
#         return ""

# # ---------- Generate Coding Question ----------
# def generate_coding_question(job_desc):
#     prompt = f"""Generate 1 Python coding question suitable for a technical interview based on the following job description: {job_desc}.
# Include:
# - Problem description
# - Input format
# - Output format
# - 2 sample test cases in this format:
# Input:
# <example input>
# Output:
# <expected output>
# """
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.7
#     }
#     try:
#         response = requests.post(url, headers=headers, json=body)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except requests.RequestException as e:
#         st.error(f"Error generating coding question: {e}")
#         return ""

# # ---------- Run Python Code using JDoodle ----------
# def run_code(code, stdin=""):
#     url = "https://api.jdoodle.com/v1/execute"
#     data = {
#         "clientId": JDoodle_CLIENT_ID,
#         "clientSecret": JDoodle_CLIENT_SECRET,
#         "script": code,
#         "language": "python3",
#         "versionIndex": "4",
#         "stdin": stdin
#     }
#     try:
#         response = requests.post(url, json=data)
#         response.raise_for_status()
#         return response.json().get("output", "❌ Execution Failed or No Output")
#     except requests.RequestException as e:
#         st.error(f"Error executing code: {e}")
#         return "❌ Execution Failed"

# # ---------- Parse MCQs ----------
# def parse_mcqs(raw_text):
#     questions = []
#     blocks = re.split(r'Q\d+\.', raw_text)
#     for block in blocks[1:]:
#         lines = block.strip().split('\n')
#         if len(lines) < 6:
#             continue
#         q_text = lines[0].strip()
#         options = [line.strip() for line in lines[1:5] if re.match(r'^[A-D]\.', line)]
#         answer_line = next((line for line in lines if line.lower().startswith("answer:")), None)
#         if answer_line and len(options) == 4:
#             correct = answer_line.split(":")[1].strip().upper()
#             questions.append({
#                 "question": q_text,
#                 "options": options,
#                 "answer": correct
#             })
#     return questions

# # ---------- Streamlit UI ----------
# st.set_page_config(page_title="Mock Interview", layout="wide")
# st.title("💼 AI-Powered Mock Interview Platform")

# if "step" not in st.session_state:
#     st.session_state.step = 0
#     st.session_state.score = 0
#     st.session_state.timer_start = None
#     st.session_state.mcqs = []
#     st.session_state.user_answers = []
#     st.session_state.code_question = ""
#     st.session_state.test_cases = []

# # ---------- Job Description Input ----------
# job_desc = st.text_area("📄 Enter Job Description:", height=100)

# if st.button("🎯 Generate Mock Interview") and job_desc:
#     with st.spinner("Generating MCQs and coding question..."):
#         mcqs_raw = generate_mcqs(job_desc)
#         st.session_state.mcqs = parse_mcqs(mcqs_raw)
#         st.session_state.user_answers = [None] * len(st.session_state.mcqs)
#         st.session_state.code_question = generate_coding_question(job_desc)
#         # Extract test cases from coding question
#         test_cases = []
#         test_blocks = re.findall(r'Input:\n(.*?)\nOutput:\n(.*?)(?=\n\n|$)', st.session_state.code_question, re.DOTALL)
#         for inp, out in test_blocks:
#             test_cases.append({"input": inp.strip(), "output": out.strip()})
#         st.session_state.test_cases = test_cases
#         st.session_state.step = 1
#         st.rerun()

# # ---------- MCQ Round ----------
# if st.session_state.step == 1:
#     st.header("🧠 MCQ Round")
#     if not st.session_state.mcqs:
#         st.error("No MCQs generated. Please try again.")
#     else:
#         for idx, q in enumerate(st.session_state.mcqs):
#             st.subheader(f"Q{idx+1}. {q['question']}")
#             st.session_state.user_answers[idx] = st.radio(
#                 "Choose your answer:",
#                 options=q["options"],
#                 key=f"q_{idx}",
#                 index=None
#             )

#         if st.button("✅ Submit MCQ Answers"):
#             if None in st.session_state.user_answers:
#                 st.warning("Please answer all questions before submitting.")
#             else:
#                 correct = 0
#                 for idx, q in enumerate(st.session_state.mcqs):
#                     selected = st.session_state.user_answers[idx]
#                     if selected and selected.startswith(f"{q['answer']}."):
#                         correct += 1
#                 st.session_state.score += correct * 10
#                 st.success(f"✅ You got {correct} out of {len(st.session_state.mcqs)} correct! Score: {correct * 10}")
#                 st.session_state.step = 2
#                 st.rerun()

# # ---------- Coding Round ----------
# if st.session_state.step == 2:
#     st.header("💻 Coding Round")
#     col1, col2 = st.columns([2, 3])

#     with col1:
#         st.markdown("### 📘 Question")
#         st.markdown(st.session_state.code_question)

#     with col2:
#         st.markdown("### ✍️ Code Editor")
#         code_input = st.text_area("Write your Python code here:", height=250, key="code_area")

#         st.markdown("### 🧪 Test Cases")
#         test_inputs = st.text_area(
#             "Input Cases",
#             value="\n".join([tc["input"] for tc in st.session_state.test_cases]),
#             height=100
#         )
#         expected_outputs = st.text_area(
#             "Expected Outputs",
#             value="\n".join([tc["output"] for tc in st.session_state.test_cases]),
#             height=100
#         )

#         if st.session_state.timer_start is None:
#             if st.button("⏳ Start Coding Timer"):
#                 st.session_state.timer_start = time.time()
#                 st.rerun()
#         else:
#             elapsed = int(time.time() - st.session_state.timer_start)
#             remaining = max(0, 300 - elapsed)
#             st.info(f"⏳ Time Remaining: {remaining // 60}:{remaining % 60:02d}")

#         col_run, col_submit, col_end = st.columns([1, 1, 1])
#         run_clicked = col_run.button("🧪 Run Code")
#         submit_clicked = col_submit.button("✅ Submit Code")
#         end_clicked = col_end.button("🚪 End Test")

#         if run_clicked and code_input:
#             st.markdown("### 🔍 Output Comparison")
#             inputs = test_inputs.strip().splitlines()
#             expected = expected_outputs.strip().splitlines()
#             for i, (inp, exp) in enumerate(zip(inputs, expected)):
#                 result = run_code(code_input, inp).strip()
#                 st.code(f"Test Case {i+1}:\nInput: {inp}\nExpected: {exp}\nYour Output: {result}")

#         if submit_clicked and code_input:
#             if remaining <= 0:
#                 st.warning("⏰ Time's up!")
#             inputs = test_inputs.strip().splitlines()
#             expected = expected_outputs.strip().splitlines()
#             if len(inputs) != len(expected):
#                 st.error("Number of inputs and expected outputs must match.")
#             else:
#                 passed = 0
#                 for inp, exp in zip(inputs, expected):
#                     result = run_code(code_input, inp).strip()
#                     if result == exp.strip():
#                         passed += 1
#                 score = 20 if passed == len(expected) else 0
#                 st.session_state.score += score
#                 if score > 0:
#                     st.success(f"✅ All test cases passed! {score} points awarded.")
#                 else:
#                     st.warning("❌ Some test cases failed. No points awarded.")
#                 st.session_state.step = 3
#                 st.rerun()

#         if end_clicked:
#             st.session_state.step = 3
#             st.rerun()

# # ---------- Final Result ----------
# if st.session_state.step == 3:
#     st.header("🎓 Interview Summary")
#     st.success(f"🏆 Final Score: {st.session_state.score} / 50")
#     if st.button("🔁 Restart"):
#         for key in list(st.session_state.keys()):
#             del st.session_state[key]
#         st.rerun()




# import streamlit as st
# import requests
# import time
# import re
# import os
# import json

# # ---------- API Keys ----------
# GROQ_API_KEY = "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"
# JDoodle_CLIENT_ID = "d3c56d56b7011b33205be169ebe24eaf"
# JDoodle_CLIENT_SECRET = "4a321690766787f5afbf1937b6acd531785833a39fbc932733592e83de6d15a8"

# # ---------- Generate MCQs from Groq ----------
# def generate_mcqs(job_desc):
#     prompt = f"""Generate 5 technical multiple-choice questions (MCQs) with 4 options (A to D) and provide the correct answer for each.
# Job Description: {job_desc}
# Format:
# Q1. ...
# A. ...
# B. ...
# C. ...
# D. ...
# Answer: B
# Q2. ...
# ..."""
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.7
#     }
#     try:
#         response = requests.post(url, headers=headers, json=body)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except requests.RequestException as e:
#         st.error(f"Error generating MCQs: {e}")
#         return ""

# # ---------- Generate Coding Question ----------
# def generate_coding_question(job_desc):
#     prompt = f"""Generate 1 coding question suitable for a technical interview based on the following job description: {job_desc}.
# Include:
# - Problem description
# - Input format
# - Output format
# - 2 sample test cases in this format:
# Input:
# <example input>
# Output:
# <expected output>
# """
#     url = "https://api.groq.com/openai/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     body = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [{"role": "user", "content": prompt}],
#         "temperature": 0.7
#     }
#     try:
#         response = requests.post(url, headers=headers, json=body)
#         response.raise_for_status()
#         return response.json()["choices"][0]["message"]["content"]
#     except requests.RequestException as e:
#         st.error(f"Error generating coding question: {e}")
#         return ""

# # ---------- Run Code using JDoodle ----------
# def run_code(code, language="python3", stdin=""):
#     version_map = {"python3": "4", "c": "5", "cpp": "5", "java": "4"}
#     url = "https://api.jdoodle.com/v1/execute"
#     data = {
#         "clientId": JDoodle_CLIENT_ID,
#         "clientSecret": JDoodle_CLIENT_SECRET,
#         "script": code,
#         "language": language,
#         "versionIndex": version_map.get(language, "4"),
#         "stdin": stdin
#     }
#     try:
#         response = requests.post(url, json=data)
#         response.raise_for_status()
#         return response.json().get("output", "❌ Execution Failed or No Output")
#     except requests.RequestException as e:
#         st.error(f"Error executing code: {e}")
#         return "❌ Execution Failed"

# # ---------- Parse MCQs ----------
# def parse_mcqs(raw_text):
#     questions = []
#     blocks = re.split(r'Q\d+\.', raw_text)
#     for block in blocks[1:]:
#         lines = block.strip().split('\n')
#         if len(lines) < 6:
#             continue
#         q_text = lines[0].strip()
#         options = [line.strip() for line in lines[1:5] if re.match(r'^[A-D]\.', line)]
#         answer_line = next((line for line in lines if line.lower().startswith("answer:")), None)
#         if answer_line and len(options) == 4:
#             correct = answer_line.split(":")[1].strip().upper()
#             questions.append({
#                 "question": q_text,
#                 "options": options,
#                 "answer": correct
#             })
#     return questions

# # ---------- Streamlit UI ----------
# st.set_page_config(page_title="Mock Interview", layout="wide")
# st.title("💼 AI-Powered Mock Interview Platform")

# if "step" not in st.session_state:
#     st.session_state.step = 0
#     st.session_state.score = 0
#     st.session_state.timer_start = None
#     st.session_state.mcqs = []
#     st.session_state.user_answers = []
#     st.session_state.code_question = ""
#     st.session_state.test_cases = []

# # ---------- Job Description Input ----------
# job_desc = st.text_area("📄 Enter Job Description:", height=100)

# if st.button("🎯 Generate Mock Interview") and job_desc:
#     with st.spinner("Generating MCQs and coding question..."):
#         mcqs_raw = generate_mcqs(job_desc)
#         st.session_state.mcqs = parse_mcqs(mcqs_raw)
#         st.session_state.user_answers = [None] * len(st.session_state.mcqs)
#         st.session_state.code_question = generate_coding_question(job_desc)

#         # Extract test cases from coding question
#         test_cases = []
#         test_blocks = re.findall(r'Input:\n(.*?)\nOutput:\n(.*?)(?=\n\n|$)', st.session_state.code_question, re.DOTALL)
#         for inp, out in test_blocks:
#             test_cases.append({"input": inp.strip(), "output": out.strip()})
#         st.session_state.test_cases = test_cases
#         st.session_state.step = 1
#         st.rerun()

# # ---------- MCQ Round ----------
# if st.session_state.step == 1:
#     st.header("🧠 MCQ Round")
#     if not st.session_state.mcqs:
#         st.error("No MCQs generated. Please try again.")
#     else:
#         for idx, q in enumerate(st.session_state.mcqs):
#             st.subheader(f"Q{idx+1}. {q['question']}")
#             st.session_state.user_answers[idx] = st.radio(
#                 "Choose your answer:",
#                 options=q["options"],
#                 key=f"q_{idx}",
#                 index=None
#             )

#         if st.button("✅ Submit MCQ Answers"):
#             if None in st.session_state.user_answers:
#                 st.warning("Please answer all questions before submitting.")
#             else:
#                 correct = 0
#                 for idx, q in enumerate(st.session_state.mcqs):
#                     selected = st.session_state.user_answers[idx]
#                     if selected and selected.startswith(f"{q['answer']}."):
#                         correct += 1
#                 st.session_state.score += correct * 10
#                 st.success(f"✅ You got {correct} out of {len(st.session_state.mcqs)} correct! Score: {correct * 10}")
#                 st.session_state.step = 2
#                 st.rerun()

# # ---------- Coding Round ----------
# if st.session_state.step == 2:
#     st.header("💻 Coding Round")
#     col1, col2 = st.columns([2, 3])

#     with col1:
#         st.markdown("### 📘 Question")
#         st.markdown(st.session_state.code_question)

#     with col2:
#         st.markdown("### ✍️ Code Editor")
#         language = st.selectbox("Select Language:", ["python3", "c", "cpp", "java"])
#         code_input = st.text_area("Write your code here:", height=250, key="code_area")

#         st.markdown("### 🧪 Test Cases")
#         test_inputs = st.text_area(
#             "Input Cases",
#             value="\n".join([tc["input"] for tc in st.session_state.test_cases]),
#             height=100
#         )
#         expected_outputs = st.text_area(
#             "Expected Outputs",
#             value="\n".join([tc["output"] for tc in st.session_state.test_cases]),
#             height=100
#         )

#         if st.session_state.timer_start is None:
#             if st.button("⏳ Start Coding Timer"):
#                 st.session_state.timer_start = time.time()
#                 st.rerun()
#         else:
#             elapsed = int(time.time() - st.session_state.timer_start)
#             remaining = max(0, 300 - elapsed)
#             st.info(f"⏳ Time Remaining: {remaining // 60}:{remaining % 60:02d}")

#         col_run, col_submit, col_end = st.columns([1, 1, 1])
#         run_clicked = col_run.button("🧪 Run Code")
#         submit_clicked = col_submit.button("✅ Submit Code")
#         end_clicked = col_end.button("🚪 End Test")

#         if run_clicked and code_input:
#             st.markdown("### 🔍 Output Comparison")
#             inputs = test_inputs.strip().splitlines()
#             expected = expected_outputs.strip().splitlines()
#             for i, (inp, exp) in enumerate(zip(inputs, expected)):
#                 result = run_code(code_input, language, inp).strip()
#                 st.code(f"Test Case {i+1}:\nInput: {inp}\nExpected: {exp}\nYour Output: {result}")

#         if submit_clicked and code_input:
#             if remaining <= 0:
#                 st.warning("⏰ Time's up!")
#             inputs = test_inputs.strip().splitlines()
#             expected = expected_outputs.strip().splitlines()
#             if len(inputs) != len(expected):
#                 st.error("Number of inputs and expected outputs must match.")
#             else:
#                 passed = 0
#                 for inp, exp in zip(inputs, expected):
#                     result = run_code(code_input, language, inp).strip()
#                     if result == exp.strip():
#                         passed += 1
#                 score = 20 if passed == len(expected) else 0
#                 st.session_state.score += score
#                 if score > 0:
#                     st.success(f"✅ All test cases passed! {score} points awarded.")
#                 else:
#                     st.warning("❌ Some test cases failed. No points awarded.")
#                 st.session_state.step = 3
#                 st.rerun()

#         if end_clicked:
#             st.session_state.step = 3
#             st.rerun()

# # ---------- Final Result ----------
# if st.session_state.step == 3:
#     st.header("🎓 Interview Summary")
#     st.success(f"🏆 Final Score: {st.session_state.score} / 50")
#     if st.button("🔁 Restart"):
#         for key in list(st.session_state.keys()):
#             del st.session_state[key]
#         st.rerun()



import streamlit as st
import serpapi as sp
import requests
import time
import re

# ---------- API Keys ----------
GROQ_API_KEY = "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"
JDoodle_CLIENT_ID = "d3c56d56b7011b33205be169ebe24eaf"
JDoodle_CLIENT_SECRET = "4a321690766787f5afbf1937b6acd531785833a39fbc932733592e83de6d15a8"

# ---------- Generate MCQs ----------
def generate_mcqs(job_desc):
    prompt = f"""Generate 10 technical multiple-choice questions (MCQs) with 4 options (A to D) and provide the correct answer for each.
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
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error generating MCQs: {e}")
        return ""

# ---------- Generate Coding Questions ----------
def generate_coding_questions(job_desc):
    prompt = f"""Generate 2 coding questions suitable for a technical interview based on the following job description: {job_desc}.
For each question, include:
- Problem description
- Input format
- Output format
- 2 sample test cases
Format:
Q1:
Problem:
Input:
Output:
Sample Input:
Sample Output:
Q2:
..."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error generating coding questions: {e}")
        return ""

# ---------- Run Code ----------
def run_code(code, language="python3", stdin=""):
    version_map = {"python3": "4", "c": "5", "cpp": "5", "java": "4"}
    url = "https://api.jdoodle.com/v1/execute"
    data = {
        "clientId": JDoodle_CLIENT_ID,
        "clientSecret": JDoodle_CLIENT_SECRET,
        "script": code,
        "language": language,
        "versionIndex": version_map.get(language, "4"),
        "stdin": stdin
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get("output", "❌ Execution Failed or No Output")
    except Exception as e:
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
            questions.append({"question": q_text, "options": options, "answer": correct})
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
    st.session_state.code_questions = []
    st.session_state.test_cases = []

# ---------- Job Description ----------
job_desc = st.text_area("📄 Enter Job Description:", height=100)

if st.button("🎯 Generate Mock Interview") and job_desc:
    with st.spinner("Generating MCQs and coding questions..."):
        # MCQs
        mcqs_raw = generate_mcqs(job_desc)
        st.session_state.mcqs = parse_mcqs(mcqs_raw)
        st.session_state.user_answers = [None] * len(st.session_state.mcqs)

        # Coding Questions
        code_raw = generate_coding_questions(job_desc)
        code_blocks = re.split(r'Q\d+:', code_raw)[1:]
        st.session_state.code_questions = [block.strip() for block in code_blocks]

        # Extract test cases
        test_cases_all = []
        for code_q in st.session_state.code_questions:
            test_blocks = re.findall(r'Sample Input:\n(.*?)\nSample Output:\n(.*?)(?=\n\n|$)', code_q, re.DOTALL)
            test_cases = [{"input": inp.strip(), "output": out.strip()} for inp, out in test_blocks]
            test_cases_all.append(test_cases)
        st.session_state.test_cases = test_cases_all

        st.session_state.step = 1
        st.rerun()

# ---------- MCQ Round ----------
if st.session_state.step == 1:
    st.header("🧠 MCQ Round")
    if not st.session_state.mcqs:
        st.error("No MCQs generated. Please try again.")
    else:
        for idx, q in enumerate(st.session_state.mcqs):
            st.markdown("---")
            st.subheader(f"Q{idx+1}. {q['question']}")
            st.session_state.user_answers[idx] = st.radio(
                "Choose your answer:",
                options=q["options"],
                key=f"q_{idx}",
                index=None
            )
        st.markdown("---")
        if st.button("✅ Submit MCQ Answers"):
            if None in st.session_state.user_answers:
                st.warning("Please answer all questions before submitting.")
            else:
                correct = sum(1 for idx, q in enumerate(st.session_state.mcqs)
                              if st.session_state.user_answers[idx].startswith(f"{q['answer']}."))
                st.session_state.score += correct * 5
                st.success(f"✅ You got {correct} out of {len(st.session_state.mcqs)} correct! Score: {correct * 5}")
                st.session_state.step = 2
                st.rerun()

# ---------- Coding Round ----------

if st.session_state.step == 2:
    st.header("💻 Coding Round")

    # Language selection
    language = st.selectbox("Select Language:", ["python3", "c", "cpp", "java"])

    # Loop through 2 coding questions
    for q_idx in range(2):
        st.markdown(f"### Question {q_idx+1}")

        # Two-column layout: Question left, Code Editor right
        col_question, col_code = st.columns([2, 3])

        with col_question:
            st.markdown("#### 📘 Question Description")
            st.markdown(st.session_state.code_questions[q_idx])

            st.markdown("#### 🧪 Sample Test Cases")
            for t_idx, tc in enumerate(st.session_state.test_cases[q_idx]):
                st.markdown(f"**Test Case {t_idx+1}**")
                st.markdown(f"**Input:**\n```text\n{tc['input']}\n```")
                st.markdown(f"**Expected Output:**\n```text\n{tc['output']}\n```")

        with col_code:
            st.markdown("#### ✍️ Code Editor")
            code_input = st.text_area(
                f"Write your code for Question {q_idx+1} here:",
                height=250,
                key=f"code_area_{q_idx}"
            )

            # Run / Submit buttons
            col_run, col_submit = st.columns([1, 1])
            run_clicked = col_run.button(f"🧪 Run Question {q_idx+1}", key=f"run_{q_idx}")
            submit_clicked = col_submit.button(f"✅ Submit Question {q_idx+1}", key=f"submit_{q_idx}")

            # Run code per test case
            if run_clicked:
                st.markdown("#### 🔍 Output Comparison")
                for t_idx, tc in enumerate(st.session_state.test_cases[q_idx]):
                    result = run_code(code_input, language, tc["input"]).strip()
                    st.code(
                        f"Test Case {t_idx+1}:\n"
                        f"Input:\n{tc['input']}\n\n"
                        f"Expected Output:\n{tc['output']}\n\n"
                        f"Your Output:\n{result}"
                    )

            # Submit code and update score
            if submit_clicked:
                passed = 0
                for t_idx, tc in enumerate(st.session_state.test_cases[q_idx]):
                    result = run_code(code_input, language, tc["input"]).strip()
                    if result == tc["output"].strip():
                        passed += 1
                score = 10 if passed == len(st.session_state.test_cases[q_idx]) else 0
                st.session_state.score += score
                if score > 0:
                    st.success(f"✅ Question {q_idx+1}: All test cases passed! {score} points awarded.")
                else:
                    st.warning(f"❌ Question {q_idx+1}: Some test cases failed. No points awarded.")

    # End coding round
    if st.button("🚪 End Coding Round"):
        st.session_state.step = 3
        st.success(f"🏁 Coding Round Completed! Final Score: {st.session_state.score}")
        st.rerun()

# ---------- Final Results ----------
if st.session_state.step == 3:
    st.header("🏁 Interview Completed!")

    total_mcq = len(st.session_state.mcqs)
    mcq_score = total_mcq * 5  # each 5 points
    coding_score = 2 * 10      # 10 points each question

    st.subheader("📊 Final Results Summary")
    st.write(f"**Total MCQ Questions:** {total_mcq}")
    st.write(f"**Total Coding Questions:** 2")
    st.write(f"**Maximum Possible Score:** {mcq_score + coding_score}")
    st.write(f"**Your Final Score:** 🏆 {st.session_state.score}")

    # Performance evaluation
    if st.session_state.score >= (0.8 * (mcq_score + coding_score)):
        st.success("🌟 Excellent performance! You’re interview-ready.")
    elif st.session_state.score >= (0.5 * (mcq_score + coding_score)):
        st.info("👍 Good job! You’re halfway there.")
    else:
        st.warning("📘 Keep practicing! Review topics and try again.")

    # Restart option
    if st.button("🔄 Restart Mock Interview"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()



# if st.session_state.step == 2:
#     st.header("💻 Coding Round")

#     # Language selection
#     language = st.selectbox("Select Language:", ["python3", "c", "cpp", "java"])

#     # Loop through 2 coding questions
#     for q_idx in range(2):
#         st.markdown(f"### Question {q_idx+1}")

#         # Two-column layout: Question left, Code Editor right
#         col_question, col_code = st.columns([2, 3])

#         with col_question:
#             st.markdown("#### 📘 Question Description")
#             st.markdown(st.session_state.code_questions[q_idx])

#             st.markdown("#### 🧪 Sample Test Cases")
#             for t_idx, tc in enumerate(st.session_state.test_cases[q_idx]):
#                 st.markdown(f"**Test Case {t_idx+1}**")
#                 st.markdown(f"**Input:**\n```text\n{tc['input']}\n```")
#                 st.markdown(f"**Expected Output:**\n```text\n{tc['output']}\n```")

#         with col_code:
#             st.markdown("#### ✍️ Code Editor")
#             code_input = st.text_area(
#                 f"Write your code for Question {q_idx+1} here:",
#                 height=250,
#                 key=f"code_area_{q_idx}"
#             )

#             # Run / Submit buttons
#             col_run, col_submit = st.columns([1, 1])
#             run_clicked = col_run.button(f"🧪 Run Question {q_idx+1}", key=f"run_{q_idx}")
#             submit_clicked = col_submit.button(f"✅ Submit Question {q_idx+1}", key=f"submit_{q_idx}")

#             # Run code per test case
#             if run_clicked:
#                 st.markdown("#### 🔍 Output Comparison")
#                 for t_idx, tc in enumerate(st.session_state.test_cases[q_idx]):
#                     result = run_code(code_input, language, tc["input"]).strip()
#                     st.code(
#                         f"Test Case {t_idx+1}:\n"
#                         f"Input:\n{tc['input']}\n\n"
#                         f"Expected Output:\n{tc['output']}\n\n"
#                         f"Your Output:\n{result}"
#                     )

#             # Submit code and update score
#             if submit_clicked:
#                 passed = 0
#                 for t_idx, tc in enumerate(st.session_state.test_cases[q_idx]):
#                     result = run_code(code_input, language, tc["input"]).strip()
#                     if result == tc["output"].strip():
#                         passed += 1
#                 score = 10 if passed == len(st.session_state.test_cases[q_idx]) else 0
#                 st.session_state.score += score
#                 if score > 0:
#                     st.success(f"✅ Question {q_idx+1}: All test cases passed! {score} points awarded.")
#                 else:
#                     st.warning(f"❌ Question {q_idx+1}: Some test cases failed. No points awarded.")

#     # End coding round
#     if st.button("🚪 End Coding Round"):
#         st.session_state.step = 3
#         st.rerun()
