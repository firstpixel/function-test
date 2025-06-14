Absolutely! Based on the full scope of our chat and the detailed functionality you’ve built, here’s a polished **`README.md`** you can use directly in your `function_test` project repository:

---

# 📊 LLM Function Analysis Grid (`function_test`)

**A Streamlit-based interactive tool to evaluate how accurately multiple LLMs call structured functions for specific tasks.**

---

## 🚀 Overview

This project is designed to **test, compare, and benchmark multiple LLM models** (served locally via [Ollama](https://ollama.com/)) on their ability to **parse natural language tasks** and return **structured function calls** matching an expected sequence.

The system provides:

* ✅ A prompt & system prompt editor with examples.
* ✅ A function selection panel to define the **exact functions** the LLM should infer.
* ✅ An execution grid that tests each available LLM **one by one**.
* ✅ Detailed timing: individual execution time, cumulative total time, and the timestamp of each run.
* ✅ An automatic success check: compares the LLM's output to the required list of functions.
* ✅ A **success percentage** per LLM, accumulated across multiple runs.
* ✅ **Dynamic coloring**: the success rate column uses a red-to-green gradient for quick visual benchmarking.
* ✅ Sorting and filtering: powered by **AgGrid**, supporting full interactivity.

---

## 🧩 How It Works

### 1️⃣ **Define Your Tasks**

You write a natural language prompt describing a list of tasks. Example:

```plaintext
1. Calculate the total of 23 + 7.
2. Open the file main.py.
3. Review the code.
...
```

### 2️⃣ **Set the System Instructions**

Provide a clear system prompt instructing the LLM to return **only a comma-separated list of functions** — one for each task — using your predefined function vocabulary.

### 3️⃣ **Select Required Functions**

Pick the exact functions you expect the LLM to call, e.g.:

* `func_calculate`
* `func_open`
* `func_develop`
* `func_save`
* `func_test`
* `func_git`
* `func_document`
* `func_weather`

### 4️⃣ **Run the Analysis**

Click **Run Analysis**:

* The tool queries **each LLM** available in your Ollama local server.
* It captures response time, checks if all required functions were included, and updates the results table.

### 5️⃣ **Inspect Results**

The AgGrid shows:

| LLM Name | Time to Execute | Total Time | Last Execution | Last Assistant Response | Success/Fail | Run Count | Success Percentage |
| -------- | --------------- | ---------- | -------------- | ----------------------- | ------------ | --------- | ------------------ |

The **Success Percentage** uses a continuous gradient:

* 🔴 Red = 0% success
* 🟢 Green = 100% success

---

## ⚡️ What It Tests

This tool specifically measures:

* Whether an LLM can interpret multiple tasks **step-by-step**.
* Whether it obeys strict output formatting (e.g., returns only a clean list with no extra text).
* How robust it is to **ambiguous tasks** (like mixed weather vs. calculation tasks).
* How consistent its performance is across repeated runs.
* Which model performs best at structured reasoning for automation agents.

---

## 🗂️ Technologies Used

* [Streamlit](https://streamlit.io) — Front-end + UI
* [Ollama Python Client](https://ollama.com) — Local LLM serving
* [AgGrid for Streamlit](https://pypi.org/project/streamlit-aggrid/) — Interactive, sortable, and styled data table
* `pandas` — For result tracking and dynamic updating

---

## ⚙️ Requirements

✅ Python 3.10+
✅ [Ollama](https://ollama.com) running locally with your LLMs installed
✅ Install dependencies:

```bash
pip install streamlit ollama streamlit-aggrid pandas matplotlib
```

---

## 📌 Project Structure

```
function_test/
 ├── main.py          # Streamlit app
 ├── README.md        # This file
 └── requirements.txt # Optional, pin dependencies
```

---

## 🔑 Key Features

* Multi-LLM loop testing.
* Per-model performance log.
* Execution time breakdown.
* Cumulative stats: **Run count** & **success percentage**.
* Visual color gradient feedback.
* Resilient error handling.
* Works locally for quick benchmarking.

---

## 📈 Example Use Cases

* Compare custom LLM finetunes.
* Validate prompt engineering strategies.
* Debug structured output reliability.
* Test compliance for code generation assistants.
* Measure multi-step reasoning performance for agent orchestration.

---

## 💡 Future Ideas

✅ Export results as CSV/JSON
✅ Support retrying failed runs
✅ Add custom function schemas with parameter hints
✅ Benchmark against cloud LLMs side-by-side
✅ Auto-generate confusion matrices for miscalled functions

---

## 🖼️ Screenshots

### Prompt and System Prompt Example

![Prompt Example](https://github.com/firstpixel/function-test/images/prompts.png)

### Expected Result Example

![Expected Results](https://github.com/firstpixel/function-test/images/expected_results.png)

### Results Grid (10 Rounds)

![Results Grid](https://github.com/firstpixel/function-test/images/results.png)

---

## 🗂️ Repo

**Project:** `function-test`
**Status:** Prototype — extend and adapt freely!
**Author:** Gil Beyruth

---

## 📜 License

MIT — free to use, share, and modify.

