# A first LLM request

A tiny Python program that sends one question to an OpenAI model. The model can choose to call a local calculator function for arithmetic, then use its result to answer. This is a direct function-calling example, not an agent framework.

## Run it

1. Create and activate a virtual environment:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, activate it with `\.venv\Scripts\Activate.ps1`.

2. Install the dependencies:

   ```sh
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and replace the placeholder with your API key.

4. Start the program:

   ```sh
   python main.py
   ```

Type one question and press Enter. The API request uses your OpenAI account and may incur usage charges.

To run the calculator tests without making an API request:

```sh
python -m unittest
```

## What happens

## How tool calling works

1. `calculate()` in `calculator.py` safely evaluates a limited arithmetic syntax. It parses Python's expression syntax tree and only handles numeric literals, parentheses, unary signs, and `+`, `-`, `*`, and `/`. It never runs arbitrary Python code.
2. `main.py` exposes the function in the `TOOLS` list. The JSON schema tells the model the function name, what it does, and that it accepts one string named `expression`.
3. The first `responses.create()` call sends the question and tool definition. The model decides whether the tool would help. When it does, its response includes a `function_call` item with JSON arguments and a `call_id`.
4. Python reads those arguments and calls the local `calculate()` function. If the expression is invalid, Python returns a calculator error as the tool output.
5. Python sends the result back as a `function_call_output` item, linked by the same `call_id`, in a new Responses API request using `previous_response_id`.
6. The model uses that result to generate its final text. The loop also supports another tool call if the model asks for one; once a response has no function calls, the program prints `response.output_text`.

The model does not execute Python. It requests a named function and proposes arguments; your program validates and executes them. The model processes the prompt and generates a response; the program does not train a model.

## Files

- `main.py` — reads one question, gives the model a calculator tool, runs requested function calls, and prints the answer.
- `calculator.py` — implements the restricted, safe arithmetic evaluator.
- `test_calculator.py` — tests arithmetic, precedence, negative values, and rejected inputs.
- `requirements.txt` — lists the two packages needed: the OpenAI Python SDK and `python-dotenv`.
- `.env.example` — safe template showing the required environment variable. Copy it to `.env` and add your key there.
- `.gitignore` — keeps `.env`, virtual environments, and Python cache files out of version control.
- `README.md` — setup steps and a short explanation of the request flow.
