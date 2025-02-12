from autogen import AssistantAgent, UserProxyAgent

# Function to prepend line numbers to each line of the code
def prepend_line_numbers(code):
    lines = code.split("\n")
    numbered_lines = [f"#{i+1} {line}" for i, line in enumerate(lines)]
    return "\n".join(numbered_lines)

# Ollama model config
config_list = [
    {
        "model": "deepseek-r1:latest",  # Ensure correct model name
        "api_type": "ollama",
        "base_url": "http://localhost:11434/v1/",
    }
]

# Create agents
fault_identifier = AssistantAgent(
    name="fault_identifier",
    llm_config={"config_list": config_list},
    system_message="Identify faulty lines in the given code. Output the line numbers and brief fault descriptions."
)

reasoning_provider = AssistantAgent(
    name="reasoning_provider",
    llm_config={"config_list": config_list},
    system_message="Explain why the identified fault occurs and how it affects the program."
)

error_fixer = AssistantAgent(
    name="error_fixer",
    llm_config={"config_list": config_list},
    system_message="Provide a corrected version of the faulty code."
)

# User Proxy
user_proxy = UserProxyAgent(name="user_proxy", human_input_mode="NEVER", code_execution_config=False)

# Read the faulty code
input_file = "faultycode.py"
with open(input_file, "r") as file:
    faulty_code = file.read()

numbered_code = prepend_line_numbers(faulty_code)

# Step 1: Fault Identification
fault_identifier_response = user_proxy.initiate_chat(
    fault_identifier,
    message=f"Identify faults in the following code:\n{numbered_code}",
    max_turns=1
)

# Extract content safely from chat history
if fault_identifier_response.chat_history:
    fault_identification_response = fault_identifier_response.chat_history[-1]["content"].strip()
else:
    fault_identification_response = ""

print("Fault Identification Response:", fault_identification_response)

# Write fault identification to a separate file
with open("fault.txt", "w") as fault_file:
    fault_file.write(fault_identification_response)

# Step 2: Reasoning Provider
reasoning_response = user_proxy.initiate_chat(
    reasoning_provider,
    message=f"Explain the following fault:\n{fault_identification_response}",
    max_turns=1
)

# Extract content safely
if reasoning_response.chat_history:
    reasoning_response_content = reasoning_response.chat_history[-1]["content"].strip()
else:
    reasoning_response_content = ""

print("Reasoning Response:", reasoning_response_content)

# Write explanation to a separate file
with open("exp.txt", "w") as exp_file:
    exp_file.write(reasoning_response_content)

# Step 3: Error Fixer
corrected_code = user_proxy.initiate_chat(
    error_fixer,
    message=f"Fix this fault:\n{fault_identification_response}\n\nExplanation:\n{reasoning_response_content}",
    max_turns=1
)

# Extract content safely
if corrected_code.chat_history:
    corrected_code_content = corrected_code.chat_history[-1]["content"].strip()
else:
    corrected_code_content = ""

print("Corrected Code Response:", corrected_code_content)

# Write corrected code to a separate file with UTF-8 encoding
with open("corr_code.py", "w", encoding="utf-8") as corrected_file:
    corrected_file.write(corrected_code_content)


print("Fault analysis written to fault.txt")
print("Explanation written to exp.txt")
print("Corrected code written to corr_code.py")
