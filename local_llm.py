"""Send a prompt to a local Ollama model and print the reply."""

import json
import urllib.error
import urllib.request

OLLAMA_GENERATE_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llama3.2"


def ask_local_llm(prompt: str) -> str:
    """POST the prompt to Ollama and return the model's text response."""
    payload = json.dumps(
        {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_GENERATE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as error:
        raise SystemExit(
            "Could not reach Ollama at 127.0.0.1:11434. "
            "Start Ollama and pull llama3.2 first."
        ) from error

    text = body.get("response")
    if not isinstance(text, str):
        raise SystemExit("Ollama did not return a text response.")
    return text


def main() -> None:
    prompt = input("Ask a question: ").strip()
    if not prompt:
        raise SystemExit("Please enter a question.")

    print("\nResponse:")
    print(ask_local_llm(prompt))


if __name__ == "__main__":
    main()
