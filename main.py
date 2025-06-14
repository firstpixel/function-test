from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
import streamlit as st
import olloma
import time
import pandas as pd

# Initialize session state for function sequence and LLM analysis results
if "functions_to_call" not in st.session_state:
    st.session_state["functions_to_call"] = [
        "func_calculate","func_open","func_develop","func_save","func_test","func_git","func_document","func_weather","func_weather","func_calculate"
    ]

if "results" not in st.session_state:
    # Get available models from ollama list command output
    import subprocess
    olloma_list = subprocess.check_output(["ollama", "list"]).decode("utf-8")
    available_models = []
    for line in olloma_list.splitlines():
        if line.strip() and not line.startswith("NAME"):
            model_name = line.split()[0]
            if model_name not in ["nomic-embed-text:latest", "hf.co/OuteAI/OuteTTS-0.2-500M-GGUF:Q8_0"]:
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
                                 value="""You are an intelligent assistant designed to analyze tasks and return an accurate list of functions corresponding to each task. Your job is to evaluate each task individually and assign one function to each task from the predefined list below. Ensure that you only return a comma-separated list of functions, strictly following these rules:

Analyze each task carefully to determine its purpose and required action.
Assign exactly one function per task from the list below based on its description:
func_calculate: Use this for tasks involving any kind of mathematical calculation.
func_weather: Use this for tasks requesting weather reports or temperature information for a location.
func_git: Use this for tasks involving git operations such as commit, push, pull, or branch creation.
func_develop: Use this for tasks that involve writing, reviewing, or modifying code.
func_test: Use this for tasks related to testing code or software.
func_save: Use this for tasks that involve saving files or data.
func_open: Use this for tasks that involve opening files or data.
func_document: Use this for tasks that involve creating or preparing documentation.
Return only the list of functions, separated by commas, with no additional text, explanations, or formatting.
Example: If the tasks are:

Add 45 and 55.
Save the file report.txt.
Test the new feature implementation.
Commit the code to the repository.
You should return: func_calculate,func_save,func_test,func_git

Remember: Each task must correspond to one function, and the output must only contain the comma-separated function names.
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
            response = olloma.chat(
                model=llm_name,
                stream=False,
                messages=messages
            )
            end_time = time.time()
            
            # Extract response and evaluate
            last_response = response["message"]["content"].strip()
            execution_time = end_time - start_time

            # Normalize the LLM's response
            normalized_response = last_response.strip()
            if normalized_response.startswith("[") and normalized_response.endswith("]"):
                normalized_response = normalized_response[1:-1]

            response_functions = set(func.strip() for func in normalized_response.split(","))
            selected_functions = set(st.session_state["functions_to_call"])
            success = selected_functions.issubset(response_functions)

        except Exception as e:
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
            "Last Assistant Response", "Success/Fail", "Run Count", "Success Percentage"
        ]] = [
            f"{execution_time:.2f} seconds", f"{total_time:.2f} seconds", time.ctime(),
            last_response, "Success" if success else "Fail", run_count, success_percentage
        ]

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
gb.configure_default_column(editable=False, sortable=True)

# Render AgGrid with gradient coloring
AgGrid(
    st.session_state["results"],
    gridOptions=gb.build(),
    enable_enterprise_modules=False,
    allow_unsafe_jscode=True,
    height=400,
    theme="streamlit",
)




# Footer
st.write("### Instructions")
st.write("""
1. Enter a prompt and system prompt.
2. Add the functions that the LLM must call.
3. Run the analysis to evaluate each LLM against the defined inputs and functions.
""")
