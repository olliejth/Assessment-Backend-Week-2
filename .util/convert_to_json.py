"""Converts the marking .txt file to JSON."""

import json
import re

if __name__ == "__main__":

    with open("marking.txt", "r", encoding="utf-8") as f:
        data = f.read()

    tests_passed = re.search(r"(\d+) passed", data)
    tests_passed = int(tests_passed.group(1)) if tests_passed else "?"

    total_tests = re.search(r"collected (\d+) items", data)
    total_tests = int(total_tests.group(1)) if total_tests else "?"

    pylint_score = re.search(r"has been rated at (\d+\.?\d+)", data)
    pylint_score = float(pylint_score.group(1)) if pylint_score else "?"

    total_score_percent = "?"
    if all(not isinstance(s, str) for s in [tests_passed, total_tests, pylint_score]):
        total_score_percent = round((90 * (tests_passed / total_tests)) + pylint_score, 2)

    with open("marking.json", 'w', encoding="utf-8") as f:
        json.dump({
            "passing_tests": tests_passed,
            "total_tests": total_tests,
            "pylint_score": pylint_score,
            "total_score_percent": total_score_percent
        }, f, indent=4)