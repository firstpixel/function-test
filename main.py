from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import streamlit as st
import time
import pandas as pd
import ollama  # Correct import for the Ollama Python client

# Initialize session state for function sequence and LLM analysis results
if "functions_to_call" not in st.session_state:
    st.session_state["functions_to_call"] = [
        "func_calculate","func_open","func_develop","func_save","func_test","func_git","func_document","func_weather","func_weather","func_calculate"
    ]

if "results" not in st.session_state:
    # Get available models from ollama list command output
    import subprocess
    ollama_list = subprocess.check_output(["ollama", "list"]).decode("utf-8")
    available_models = []
    for line in ollama_list.splitlines():
        if line.strip() and not line.startswith("NAME"):
            model_name = line.split()[0]
            if model_name not in [
                "nomic-embed-text:latest",
                "hf.co/OuteAI/OuteTTS-0.2-500M-GGUF:Q8_0",
                "llava:latest",
                "mistral:7b",
                "deepseek-r1:14b",
                "phi4:latest",
                "deepseek-coder-v2:16b",
                "qwen2.5-coder:14b",
                "deepseek-coder:6.7b",
                "minicpm-v:latest",
                "qwen2.5:latest"
            ]:
                available_models.append(model_name)
    st.session_state["results"] = pd.DataFrame([
        {
            "LLM Name": llm_name,
            "Time to Execute": "0.00 seconds",
            "Total Time": "0.00 seconds",
            "Last Execution": "Never",
            "Last Assistant Response": "N/A",
            "Success/Fail": "N/A",
            "Run Count": 0,
            "Success Percentage": 0.0
        } for llm_name in available_models
    ])

# Page Layout
st.set_page_config(layout="wide")

# Top Section: Prompt and System Prompt
col1, col2 = st.columns(2)
with col1:
    prompt = st.text_area("Prompt", height=150, 
    value="""Tasks to Perform with Appropriate Functions

You are required to analyze and perform the following tasks. Each task must be matched with exactly one corresponding function:

1. Calculate the total of 23 + 7.
2. Open the file main.py.
3. Review the code in the file for improvements.
4. Save the updated file after making changes.
5. Test the code to ensure functionality and correctness.
6. Commit the code changes to the main branch in the Git repository.
7. Create a README.md file for documentation.
8. Provide the current temperature in São Paulo.
9. Provide the current temperature in Rio de Janeiro.
10. Calculate the average temperature between São Paulo and Rio de Janeiro.

**Instructions:**
Carefully analyze each task and select a suitable function to execute it.
Ensure tasks involving calculations, file operations, code testing, git commands, and weather information are matched with the most appropriate function.
""")
with col2:
    system_prompt = st.text_area("System Prompt", height=150, 
                                 value="""You are a highly precise task classifier.  
Your job is to read a list of tasks provided by the user and, for each task, choose **exactly one function** from the predefined list below that best describes the required action.

You MUST:
- Analyze each task one by one.
- Match each task to the most appropriate function **from the list below** — no exceptions.
- Return **only the list of function names**, in the same order as the tasks, separated by commas, with no other text or formatting.

**Available Functions:**
- func_calculate: Use if the task involves any numerical calculation or arithmetic.
- func_weather: Use if the task requests weather information or temperature for any location.
- func_git: Use if the task involves git commands like commit, push, pull, branch creation, or version control.
- func_develop: Use if the task involves writing, editing, or reviewing any code.
- func_test: Use if the task involves testing code or verifying functionality.
- func_save: Use if the task requires saving a file or data.
- func_open: Use if the task requires opening a file.
- func_document: Use if the task requests creating or updating documentation.

**Output Requirements:**
- Your final answer must contain ONLY the function names in the correct order, separated by commas.
- DO NOT include explanations, code, markdown, bullet points, or any extra words.

**Example:**
Input Tasks:  
1. Add 45 and 55  
2. Save the file report.txt  
3. Test the new feature implementation  
4. Commit the code to the repository

Expected Output:  
func_calculate,func_save,func_test,func_git

Remember: The output must be a plain comma-separated list — no brackets, quotes, or additional notes.
""")

# Function Selection Section
st.write("### Function Selection")
function_options = ["func_calculate", "func_weather", "func_git", "func_develop", 
                    "func_test", "func_save", "func_open", "func_document"]

selected_function = st.selectbox("Select a function to add", function_options)
if st.button("Add Function"):
    st.session_state["functions_to_call"].append(selected_function)

# Display current sequence of functions
st.write("#### Selected Functions Sequence")
col_func, col_clear = st.columns([3,1])
with col_func:
    st.write(st.session_state["functions_to_call"])
with col_clear:
    if st.button("Clear Functions"):
        st.session_state["functions_to_call"] = []

# Run Analysis
st.write("### LLM Analysis Grid")
if st.button("Run Analysis"):
    results_df = st.session_state["results"]
    for idx, row in results_df.iterrows():
        llm_name = row["LLM Name"]
        print(f"[DEBUG] Starting analysis for model: {llm_name}")
        start_time = time.time()
        success = True
        last_response = ""
        try:
            # Build message sequence
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            # Call the LLM
            response = ollama.chat(
                model=llm_name,
                stream=False,
                messages=messages
            )
            end_time = time.time()
            print(f"[DEBUG] Finished analysis for model: {llm_name}")
            # Extract response and evaluate
            last_response = response["message"]["content"].strip()
            execution_time = end_time - start_time

            # Normalize the LLM's response
            normalized_response = last_response.strip()
            # Remove <think>...</think> tags and their content
            import re
            normalized_response = re.sub(r'<think>.*?</think>', '', normalized_response, flags=re.DOTALL).strip()
            if normalized_response.startswith("[") and normalized_response.endswith("]"):
                normalized_response = normalized_response[1:-1]

            response_functions = [func.strip() for func in normalized_response.split(",") if func.strip()]
            selected_functions = st.session_state["functions_to_call"]
            # Validate both content and order
            success = response_functions == selected_functions

        except Exception as e:
            print(f"[DEBUG] Error during analysis for model: {llm_name}: {e}")
            success = False
            execution_time = time.time() - start_time
            last_response = f"Error: {str(e)}"

        # Update results
        total_time = float(row["Total Time"].split()[0]) + execution_time
        run_count = row["Run Count"] + 1
        success_count = row["Run Count"] * (row["Success Percentage"] / 100)
        if success:
            success_count += 1
        success_percentage = (success_count / run_count) * 100
        st.session_state["results"].loc[idx, [
            "Time to Execute", "Total Time", "Last Execution",
            "Success/Fail", "Run Count", "Success Percentage", "Last Assistant Response"
        ]] = [
            f"{execution_time:.2f} seconds", f"{total_time:.2f} seconds", time.ctime(),
            "Success" if success else "Fail", run_count, success_percentage, last_response
        ]

# Reorder columns so 'Last Assistant Response' is after 'Success Percentage'
results_df = st.session_state["results"]
if list(results_df.columns) != [
    "LLM Name", "Time to Execute", "Total Time", "Last Execution",
    "Success/Fail", "Run Count", "Success Percentage", "Last Assistant Response"
]:
    st.session_state["results"] = results_df[[
        "LLM Name", "Time to Execute", "Total Time", "Last Execution",
        "Success/Fail", "Run Count", "Success Percentage", "Last Assistant Response"
    ]]

# JavaScript function for gradient coloring
gradient_js = JsCode("""
function(params) {
    if (params.value < 50) {
        return {
            'color': 'black',
            'backgroundColor': `rgb(${255}, ${Math.round((params.value / 50) * 255)}, 0)`
        };
    } else {
        return {
            'color': 'black',
            'backgroundColor': `rgb(${Math.round((1 - (params.value - 50) / 50) * 255)}, ${255}, 0)`
        };
    }
}
""")

# Configure AgGrid with JavaScript-based gradient
gb = GridOptionsBuilder.from_dataframe(st.session_state["results"])
gb.configure_column("Success Percentage", cellStyle=gradient_js)
gb.configure_column("Last Assistant Response", width=300, resizable=True)
gb.configure_default_column(editable=False, sortable=True)

# Render AgGrid with gradient coloring
AgGrid(
    st.session_state["results"].sort_values([
        "Time to Execute", "Success Percentage"],
        ascending=[True, False],
        key=lambda col: col.str.replace(' seconds', '').astype(float) if col.name == "Time to Execute" else col
    ),
    gridOptions=gb.build(),
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True,
    height=400,
    theme="streamlit"
)
