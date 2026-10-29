import ollama
from mood_profile import recommend_from_library
DEBUG = False   # <-- 1. at the top, set once

available_tools = {"recommend_from_library": recommend_from_library}

messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly assistant that helps the user decide what to play "
            "from games they already own on Steam. "
            "When the user describes their mood or what they feel like playing, "
            "call the recommend_from_library tool and pass their mood in their own words. "
            "Then share the tool's recommendation in a friendly, natural way. "
            "Only mention games that appear in the tool's answer; never add other games. "
            "If the user only greets you or makes small talk, reply naturally without using any tools."
        ),
    }
]


def wants_games(text: str) -> bool:
    check = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Decide if the user's message asks for game suggestions or describes "
                    "what kind of game they want to play. Greetings, small talk and testing "
                    "do not count. Reply with only YES or NO."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    answer = check.message.content.strip().upper()
    if DEBUG:                                   # <-- 2. replaces the old print
        print(f"[router: {answer}]")
    return answer.startswith("YES")


greeting = "Hello! How can I help you find a game today?"   # <-- 3. greeting is back
print("AI:", greeting)
messages.append({"role": "assistant", "content": greeting})

while True:
    user_text = input("You: ")
    if user_text == "quit":
        break

    messages.append({"role": "user", "content": user_text})

    if wants_games(user_text):
        tools = [recommend_from_library]
    else:
        tools = []

    # keep going until the model stops asking for tools
    while True:
        response = ollama.chat(model="llama3.2", messages=messages, tools=tools)
        messages.append(response.message)

        if not response.message.tool_calls:
            break

        for call in response.message.tool_calls:
            name = call.function.name
            args = call.function.arguments
            if DEBUG:                           #
                print(f"[using {name} with {args}]")

            result = available_tools[name](**args)

            messages.append({"role": "tool", "content": result, "tool_name": name})

    print("AI:", response.message.content)