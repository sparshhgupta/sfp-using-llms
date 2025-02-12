from openai import OpenAI
import re

# Function to prepend line numbers to each line of the code
def prepend_line_numbers(code):
    lines = code.split("\n")
    numbered_lines = [f"#{i+1} {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered_lines)

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1/"
)

input_file = "faultycode.py"
with open(input_file, "r") as file:
    faulty_code = file.read()

numbered_code = prepend_line_numbers(faulty_code)

response = client.chat.completions.create(
    model="deepseek-r1:latest",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that identifies faults in code, explains the fault, and provides corrected versions."},
        {"role": "user", "content": f"Analyze the following code, identify the line number containing the fault, explain the fault, and provide the corrected version of the code. Line numbers are prepended as #1, #2, etc.:\n{numbered_code}"},
    ],
    stream=False,
)

# Extract the response
response_content = response.choices[0].message.content

# Write the faulty line number and explanation to fault.txt
with open("fault.txt", "w") as fault_file:
    fault_file.write(response_content)

corrected_code = response_content.split("```python")[-1].strip()

# Remove line numbers from the corrected code (if any)
corrected_code = re.search(r"```python(.*?)```", response_content, re.DOTALL)
corrected_code = corrected_code.group(1).strip() if corrected_code else ""

# Write the corrected code to correctedcode.py
with open("correctedcode.py", "w") as corrected_file:
    corrected_file.write(corrected_code)

print("Fault analysis written to fault.txt")
print("Corrected code written to correctedcode.py")