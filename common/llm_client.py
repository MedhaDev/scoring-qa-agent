"""
The ONE place that talks to an AI model.

It uses the OpenAI-compatible chat format, so the same code works with Gemini,
OpenAI or Anthropic: only API_BASE_URL, API_KEY and MODEL in .env change.

The client also keeps a running count of tokens and time for the results table.
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError

load_dotenv()

REQUEST_TIMEOUT_SECONDS = 600

# Free tiers limit requests per minute. When we hit that, wait and try again.
RATE_LIMIT_WAIT_SECONDS = 60
RATE_LIMIT_RETRIES = 5


class DailyLimitReached(Exception):
    """Raised when the provider keeps refusing requests, e.g. the daily free quota is used up."""


class LLMClient:
    def __init__(self):
        base_url = os.getenv("API_BASE_URL")
        api_key = os.getenv("API_KEY")
        model = os.getenv("MODEL")

        if not base_url or not api_key or not model:
            raise ValueError("Set API_BASE_URL, API_KEY and MODEL in .env")

        self.model = model
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)

        self.input_tokens = 0
        self.output_tokens = 0
        self.seconds = 0.0
        self.calls = 0

    def chat(self, messages, tools=None):
        """Send the conversation and return the model's reply message."""
        request = {"model": self.model, "messages": messages}
        if tools:
            request["tools"] = tools

        response = None
        for attempt in range(1, RATE_LIMIT_RETRIES + 1):
            start = time.time()
            try:
                response = self.client.chat.completions.create(**request)
                self.seconds += time.time() - start
                break
            except RateLimitError:
                print(f"    rate limit hit, waiting {RATE_LIMIT_WAIT_SECONDS}s (attempt {attempt} of {RATE_LIMIT_RETRIES})")
                time.sleep(RATE_LIMIT_WAIT_SECONDS)

        if response is None:
            raise DailyLimitReached("The provider kept refusing requests. The daily limit is probably used up; try again tomorrow.")

        self.calls += 1

        if response.usage is not None:
            self.input_tokens += response.usage.prompt_tokens or 0
            self.output_tokens += response.usage.completion_tokens or 0

        return response.choices[0].message

    def usage(self):
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "seconds": round(self.seconds, 2),
            "turns": self.calls,
        }
