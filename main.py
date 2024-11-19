import streamlit as st
import ollama
import time
import pandas as pd

# Initialize session state for the function sequence
if "functions_to_call" not in st.session_state:
    st.session_state["functions_to_call"] = []

# Page Layout
st.set_page_config(layout="wide")

# Top Section: Prompt and System Prompt
col1, col2 = st.columns(2)
with col1:
    prompt = st.text_area("Prompt", height=150, 
    value="""# Call one function for each task.
1. Calculate the total of 23 + 7
2. Open file main.py
3. Review the code
4. Save file
5. test the code
6. Commit the code in the git branch
7. Create a documentation""")
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
    if selected_function not in st.session_state["functions_to_call"]:
        st.session_state["functions_to_call"].append(selected_function)

# Display current sequence of functions
st.write("#### Selected Functions Sequence")
st.write(st.session_state["functions_to_call"])

# Grid Section: LLM Analysis
st.write("### LLM Analysis Grid")
available_models = [model["name"] for model in ollama.list()["models"]]

# Prepare a DataFrame to display results
columns = ["LLM Name", "Time to Execute", "Total Time", "Last Execution", 
           "Last Assistant Response", "Success/Fail"]
results_df = pd.DataFrame(columns=columns)

# Analyze button
if st.button("Run Analysis"):
    for llm_name in available_models:
        if llm_name != "nomic-embed-text:latest":  # Skip this specific model
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
                
                # Extract response and evaluate
                last_response = response["message"]["content"].strip()
                execution_time = end_time - start_time

                #print(f"RESPONSE {last_response}")
                selected_functions = set(st.session_state["functions_to_call"])
                #print(f"SET LIST {selected_functions}")
                # Normalize the LLM's response
                normalized_response = last_response.strip()
                if normalized_response.startswith("[") and normalized_response.endswith("]"):
                    # Remove brackets if present
                    normalized_response = normalized_response[1:-1]

                # Split by commas and trim spaces
                response_functions = set(func.strip() for func in normalized_response.split(","))
                print(f"SET RESPONSE {response_functions}")
                
                # Check if all selected functions are in the response
                success = selected_functions.issubset(response_functions)
                print(f"SUCCESS {success}")
            except Exception as e:
                success = False
                execution_time = time.time() - start_time
                last_response = f"Error: {str(e)}"

            # Add results to DataFrame
            results_df = pd.concat([
                results_df,
                pd.DataFrame([{
                    "LLM Name": llm_name,
                    "Time to Execute": f"{execution_time:.2f} seconds",
                    "Total Time": f"{execution_time:.2f} seconds",
                    "Last Execution": time.ctime(),
                    "Last Assistant Response": last_response,
                    "Success/Fail": "Success" if success else "Fail"
                }])
            ], ignore_index=True)

    # Display results in a table
    st.write("#### Results")
    st.dataframe(results_df)

# Footer
st.write("### Instructions")
st.write("""
1. Enter a prompt and system prompt.
2. Add the functions that the LLM must call.
3. Run the analysis to evaluate each LLM against the defined inputs and functions.
""")
