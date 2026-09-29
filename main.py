"""Ask a question and let the model use a local calculator when useful."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from calculator import calculate


TOOLS = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Evaluate a basic arithmetic expression when accurate calculation is useful.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "An arithmetic expression using numbers, parentheses, +, -, *, and /.",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]


def main() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Missing OPENAI_API_KEY. Add it to your .env file.")

    question = input("Ask a question: ").strip()
    if not question:
        raise SystemExit("Please enter a question.")

    client = OpenAI()
    response = client.responses.create(model="gpt-5", input=question, tools=TOOLS)

    # A response can contain one or more function calls. Run each locally, then
    # send their outputs back so the model can write its user-facing answer.
    while True:
        function_calls = [item for item in response.output if item.type == "function_call"]
        if not function_calls:
            break

        tool_outputs = []
        for function_call in function_calls:
            arguments = json.loads(function_call.arguments)
            try:
                result = calculate(arguments["expression"])
                output = str(result)
            except (KeyError, TypeError, ValueError) as error:
                output = f"Calculator error: {error}"

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": output,
                }
            )

        response = client.responses.create(
            model="gpt-5",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )

    print("\nResponse:")
    print(response.output_text)


if __name__ == "__main__":
    main()
