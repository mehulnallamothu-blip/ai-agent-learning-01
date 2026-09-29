"""A tiny educational agent: local llama3.2 plus a calculator tool."""

from calculator import calculate
from local_llm import ask_local_llm

# The model has no real tools. This text is how we teach it the contract:
# either answer the user, or request one calculator call in a fixed format.
SYSTEM_INSTRUCTIONS = """
You are a helpful assistant. You have access to one tool: a calculator
that can evaluate arithmetic using numbers, parentheses, +, -, *, and /.

If you need an exact calculation, reply with ONLY these two lines and
nothing else:

TOOL: calculator
INPUT: <arithmetic expression>

Do not solve the arithmetic yourself when you request the tool.
If you do not need the calculator, reply with the final answer for the user.
""".strip()

def parse_calculator_request(model_text: str) -> str | None:
    """Return the arithmetic expression if the model asked for the calculator.

    Local models often skip labels. Accept either:
      TOOL: calculator
      INPUT: 8400 * 0.25
    or:
      TOOL: calculator
      8400 * 0.25
    """
    lines = [line.strip() for line in model_text.splitlines() if line.strip()]

    for index, line in enumerate(lines):
        # Step A: look for the tool name, ignoring extra spaces and case.
        if line.lower().replace(" ", "") != "tool:calculator":
            continue

        # Step B: the next non-empty line is the expression.
        if index + 1 >= len(lines):
            return None
        expression_line = lines[index + 1]

        # Step C: strip INPUT: when the model included it; otherwise use the line.
        if expression_line.lower().startswith("input:"):
            expression_line = expression_line.split(":", 1)[1]

        expression = expression_line.strip()
        return expression or None

    return None


def run_calculator(expression: str) -> str:
    """Run the local calculator and turn the result (or error) into text."""
    try:
        return str(calculate(expression))
    except ValueError as error:
        return f"Calculator error: {error}"


def main() -> None:
    question = input("Ask a question: ").strip()
    if not question:
        raise SystemExit("Please enter a question.")

    # --- Agent loop, step 1: send the question to the local LLM ---
    # The model sees the tool instructions and the user question together.
    # It either answers, or asks Python to run the calculator.
    first_prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"User question:\n{question}"
    )
    first_reply = ask_local_llm(first_prompt)

    # --- Agent loop, step 2: detect a tool request in Python ---
    # The LLM cannot execute code. We parse its text and decide what to do.
    expression = parse_calculator_request(first_reply)
    if expression is None:
        # No tool request: the first reply is already the user-facing answer.
        print("\nResponse:")
        print(first_reply)
        return

    # --- Agent loop, step 3: run the tool locally ---
    tool_result = run_calculator(expression)

    # --- Agent loop, step 4: send the tool result back, ask for a final answer ---
    # A second LLM call gives the model the original question, the expression
    # it requested, and the number Python computed.
    final_prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"User question:\n{question}\n\n"
        f"You requested the calculator with:\n{expression}\n\n"
        f"Calculator result:\n{tool_result}\n\n"
        "Do not request the tool again. Write the final answer for the user."
    )
    final_reply = ask_local_llm(final_prompt)

    print("\nResponse:")
    print(final_reply)


if __name__ == "__main__":
    main()
