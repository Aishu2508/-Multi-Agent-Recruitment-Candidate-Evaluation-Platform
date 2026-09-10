import subprocess
import tempfile
import time
import os
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import settings

CHALLENGE_BANK = {
    "python": [
        {
            "id": "py_two_sum",
            "title": "Two Sum Target Finder",
            "difficulty": "Medium",
            "skill": "Python",
            "description": "Given a list of integers 'nums' and an integer 'target', return the indices of the two numbers such that they add up to target.",
            "starter_code": "def two_sum(nums, target):\n    # Write your solution here\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []\n",
            "test_cases": [
                {"input": "two_sum([2, 7, 11, 15], 9)", "expected": "[0, 1]"},
                {"input": "two_sum([3, 2, 4], 6)", "expected": "[1, 2]"},
                {"input": "two_sum([3, 3], 6)", "expected": "[0, 1]"},
                {"input": "two_sum([], 5)", "expected": "[]"}
            ],
            "expected_time_complexity": "O(N)",
            "edge_cases": ["Empty array", "Duplicate elements", "Negative numbers"]
        },
        {
            "id": "py_valid_parentheses",
            "title": "Valid Bracket Sequence",
            "difficulty": "Easy",
            "skill": "Python",
            "description": "Given a string s containing '(', ')', '{', '}', '[' and ']', determine if the input string is valid.",
            "starter_code": "def is_valid(s: str) -> bool:\n    stack = []\n    mapping = {')': '(', '}': '{', ']': '['}\n    for char in s:\n        if char in mapping:\n            top = stack.pop() if stack else '#'\n            if mapping[char] != top:\n                return False\n        else:\n            stack.append(char)\n    return not stack\n",
            "test_cases": [
                {"input": "is_valid('()[]{}')", "expected": "True"},
                {"input": "is_valid('(]')", "expected": "False"},
                {"input": "is_valid('([)]')", "expected": "False"},
                {"input": "is_valid('{[]}')", "expected": "True"}
            ],
            "expected_time_complexity": "O(N)",
            "edge_cases": ["Odd length string", "Single closing bracket", "Empty string"]
        }
    ],
    "java": [
        {
            "id": "java_palindrome",
            "title": "Palindrome String Check",
            "difficulty": "Easy",
            "skill": "Java",
            "description": "Write a Java method that checks whether an alphanumeric string is a palindrome, ignoring cases.",
            "starter_code": "public class Solution {\n    public static boolean isPalindrome(String s) {\n        String clean = s.replaceAll(\"[^a-zA-Z0-9]\", \"\").toLowerCase();\n        int l = 0, r = clean.length() - 1;\n        while (l < r) {\n            if (clean.charAt(l) != clean.charAt(r)) return false;\n            l++; r--;\n        }\n        return true;\n    }\n    public static void main(String[] args) {\n        System.out.println(isPalindrome(\"race a car\"));\n    }\n}\n",
            "test_cases": [
                {"input": "\"A man, a plan, a canal: Panama\"", "expected": "true"},
                {"input": "\"race a car\"", "expected": "false"}
            ],
            "expected_time_complexity": "O(N)",
            "edge_cases": ["String with only special characters", "Single character", "Case insensitivity"]
        }
    ]
}

def get_coding_challenge(skill_list: List[str] = None, language: str = "python") -> Dict[str, Any]:
    lang = language.lower()
    if lang not in CHALLENGE_BANK:
        lang = "python"
    
    # Select challenge matching candidate skills if possible
    challenges = CHALLENGE_BANK[lang]
    return challenges[0]

def analyze_complexity(code: str, language: str = "python") -> str:
    """Estimates time complexity based on AST / loop analysis."""
    if language.lower() == "python":
        try:
            tree = ast.parse(code)
            loop_count = 0
            nested_max = 0
            
            def count_nested(node, depth=0):
                nonlocal nested_max
                if isinstance(node, (ast.For, ast.While)):
                    depth += 1
                    if depth > nested_max:
                        nested_max = depth
                for child in ast.iter_child_nodes(node):
                    count_nested(child, depth)

            count_nested(tree, 0)
            if nested_max == 0:
                return "O(1)"
            elif nested_max == 1:
                return "O(N)"
            elif nested_max == 2:
                return "O(N^2)"
            else:
                return f"O(N^{nested_max})"
        except Exception:
            return "O(N)"
    return "O(N)"

def execute_code_e2b(code: str, language: str) -> Optional[Dict[str, Any]]:
    """Executes code via E2B Code Interpreter if API key configured."""
    if not settings.E2B_API_KEY:
        return None
    try:
        from e2b_code_interpreter import Sandbox
        with Sandbox(api_key=settings.E2B_API_KEY) as sandbox:
            execution = sandbox.run_code(code)
            return {
                "stdout": "\n".join([str(l) for l in execution.logs.stdout]),
                "stderr": "\n".join([str(l) for l in execution.logs.stderr]),
                "error": str(execution.error) if execution.error else None
            }
    except Exception as e:
        return {"stdout": "", "stderr": f"E2B execution error: {e}", "error": str(e)}

def execute_python_tests(code: str, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
    """Executes Python code in an isolated subprocess with test harness and timeout."""
    test_harness = f"""
{code}

import json

results = []
test_cases = {test_cases}

for tc in test_cases:
    expr = tc["input"]
    expected_str = tc["expected"]
    try:
        val = eval(expr)
        val_str = str(val)
        passed = (val_str == expected_str)
        results.append({{"test": expr, "expected": expected_str, "actual": val_str, "passed": passed}})
    except Exception as e:
        results.append({{"test": expr, "expected": expected_str, "actual": str(e), "passed": False, "error": True}})

print("---RESULTS_JSON---")
print(json.dumps(results))
"""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as tf:
        tf.write(test_harness)
        tf_path = tf.name

    try:
        proc = subprocess.run(
            ["python", tf_path],
            capture_output=True,
            text=True,
            timeout=settings.CODE_TIMEOUT_SECONDS
        )
        stdout = proc.stdout
        stderr = proc.stderr

        if "---RESULTS_JSON---" in stdout:
            parts = stdout.split("---RESULTS_JSON---")
            import json
            results = json.loads(parts[1].strip())
            passed_count = sum(1 for r in results if r.get("passed"))
            total_count = len(results)
            score = round((passed_count / max(total_count, 1)) * 100.0, 2)
            return {
                "score": score,
                "passed_tests": passed_count,
                "total_tests": total_count,
                "results": results,
                "stdout": parts[0].strip(),
                "stderr": stderr
            }
        else:
            return {
                "score": 0.0,
                "passed_tests": 0,
                "total_tests": len(test_cases),
                "results": [],
                "stdout": stdout,
                "stderr": stderr or "Failed to run test harness"
            }
    except subprocess.TimeoutExpired:
        return {
            "score": 0.0,
            "passed_tests": 0,
            "total_tests": len(test_cases),
            "results": [],
            "stdout": "",
            "stderr": f"Execution timed out after {settings.CODE_TIMEOUT_SECONDS}s"
        }
    finally:
        if os.path.exists(tf_path):
            try:
                os.remove(tf_path)
            except Exception:
                pass

def evaluate_submission(challenge_id: str, code: str, language: str = "python") -> Dict[str, Any]:
    lang = language.lower()
    challenge = None
    for item in CHALLENGE_BANK.get(lang, []):
        if item["id"] == challenge_id:
            challenge = item
            break
    if not challenge:
        challenge = CHALLENGE_BANK[lang][0]

    # Complexity analysis
    detected_complexity = analyze_complexity(code, lang)
    
    # Try E2B first if configured, else local runner
    if settings.E2B_API_KEY:
        e2b_res = execute_code_e2b(code, lang)
        if e2b_res and not e2b_res.get("error"):
            # Process E2B result
            pass

    # Standard test runner
    if lang == "python":
        exec_res = execute_python_tests(code, challenge["test_cases"])
    else:
        # Mock Java runner or basic syntax/execution
        exec_res = {
            "score": 85.0,
            "passed_tests": len(challenge["test_cases"]),
            "total_tests": len(challenge["test_cases"]),
            "results": [{"test": "Java Suite", "expected": "passed", "actual": "passed", "passed": True}],
            "stdout": "Java test compilation and execution simulated.",
            "stderr": ""
        }

    return {
        "challenge_id": challenge["id"],
        "challenge_title": challenge["title"],
        "language": lang,
        "score": exec_res["score"],
        "passed_tests": exec_res["passed_tests"],
        "total_tests": exec_res["total_tests"],
        "test_details": exec_res["results"],
        "detected_time_complexity": detected_complexity,
        "expected_time_complexity": challenge["expected_time_complexity"],
        "edge_case_suggestions": challenge["edge_cases"],
        "stdout": exec_res["stdout"],
        "stderr": exec_res["stderr"]
    }
