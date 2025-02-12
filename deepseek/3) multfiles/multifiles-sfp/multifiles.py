import os
import subprocess
import re
from openai import OpenAI

# OpenAI Client (Local Model like DeepSeek, Code Llama, or Ollama)
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1/"
)

# Function to detect language based on file extension
def detect_language(file_path: str) -> str | None:
    ext = os.path.splitext(file_path)[-1]
    return {
        ".py": "python",
        ".c": "c",
        ".cpp": "cpp",
        ".js": "javascript",
        ".java": "java"
    }.get(ext, None)

# Function to run linters, type checkers, or analyzers based on language
def run_checker(file_path: str, lang: str) -> str | None:
    print(f"🔍 Running checker for: {file_path} ({lang})")
    
    try:
        if lang == "python":
            lint_result = subprocess.run(["flake8", file_path], capture_output=True, text=True)
            type_result = subprocess.run(["mypy", file_path], capture_output=True, text=True)
            output = lint_result.stdout + "\n" + type_result.stdout
        elif lang == "c":
            output = subprocess.run(["clang-tidy", file_path, "--", "-std=c11"], capture_output=True, text=True).stdout
        elif lang == "cpp":
            output = subprocess.run(["clang-tidy", file_path, "--", "-std=c++17"], capture_output=True, text=True).stdout
        # elif lang == "java":
        #     output = subprocess.run(["checkstyle", "-c", "/google_checks.xml", file_path], capture_output=True, text=True).stdout
        else:
            print(f"Unsupported language for {file_path}")
            return None  

        if output.strip():
            print(f"Issues detected in {file_path}:\n{output}")
        else:
            print(f"No linter/type issues found in {file_path}")

        return output if output.strip() else None  
    except Exception as e:
        print(f"Error running checker for {file_path}: {str(e)}")
        return f"Error running checker: {str(e)}"

# Function to prepend line numbers to code
def prepend_line_numbers(code: str) -> str:
    lines = code.split("\n")
    return "\n".join([f"#{i+1} {line}" for i, line in enumerate(lines)])

# Function to analyze faults with LLM
def analyze_with_llm(file_path: str, code: str) -> str | None:
    print(f"Analyzing {file_path} with LLM...")
    numbered_code = prepend_line_numbers(code)
    
    response = client.chat.completions.create(
        model="deepseek-r1:latest",
        messages=[
            {"role": "system", "content": "You are an AI that predicts software faults, provides explanations, and corrects errors."},
            {"role": "user", "content": f"Analyze the following code and predict faults. Identify faulty lines, and explain the potential issues:\n{numbered_code}"}
        ],
        stream=True,  # Streaming enabled
    )

    llm_response = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            llm_response += chunk.choices[0].delta.content

    print("\nLLM Analysis Completed!")
    return llm_response if llm_response.strip() else None

# Function to scan an entire project directory for faulty files
def scan_project(project_dir: str) -> dict:
    print(f"Scanning project directory: {project_dir}")
    faulty_files = {}

    for root, _, files in os.walk(project_dir):
        for file in files:
            file_path = os.path.join(root, file)
            lang = detect_language(file_path)

            if lang:
                print(f"Processing {file_path} ({lang})...")
                
                # 1️⃣ Run Linters & Type Checkers (Initial Check)
                checker_output = run_checker(file_path, lang)

                # 2️⃣ Read Code File
                with open(file_path, "r") as f:
                    code = f.read()

                # 3️⃣ Run LLM Fault Prediction (Catches Logical Errors Too)
                llm_analysis = analyze_with_llm(file_path, code)

                # Store results if faults are found
                if checker_output or llm_analysis:
                    faulty_files[file_path] = {
                        "checker_issues": checker_output or "No linter/type issues found.",
                        "llm_analysis": llm_analysis or "No LLM faults detected."
                    }

    print(f"Scanning completed. {len(faulty_files)} files with issues found.")
    return faulty_files

# Function to save analysis report
def save_report(faulty_files: dict, output_dir: str = "fault_reports") -> None:
    os.makedirs(output_dir, exist_ok=True)
    print(f"Saving reports to {output_dir}...")

    for file_path, analysis in faulty_files.items():
        file_name = os.path.basename(file_path)
        report_path = os.path.join(output_dir, f"{file_name}_faults.txt")

        with open(report_path, "w") as f:
            f.write(f"Checker Issues:\n{analysis['checker_issues']}\n\nLLM Analysis:\n{analysis['llm_analysis']}\n")

        print(f"Report saved: {report_path}")

# Main Execution
project_directory = "testproject"  # Change this to your actual project path
faults = scan_project(project_directory)
save_report(faults)

print("Fault analysis completed. Reports saved in 'fault_reports' directory.")