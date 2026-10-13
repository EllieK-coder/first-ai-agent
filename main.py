import ollama
from SteamSpy import find_games_by_tag

DEBUG = False   # <-- 1. at the top, set once

available_tools = {"find_games_by_tag": find_games_by_tag}

messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly assistant that helps the user pick a Steam game. "
            "First chat with them to understand their mood and what they feel like playing. "
            "Only use the find_games_by_tag tool once you know what kind of game they want. "
            "Use Steam tag names like Relaxing, Roguelike, Puzzle, Horror, Open World, Co-op. "
            "From the results, recommend 1 to 3 games and explain why they fit. "
            "If the user only greets you or makes small talk, reply naturally and do not use any tools."
        ),
    }
]


def wants_games(text: str) -> bool:
    check = ollama.chat(
        model="llama3.2",
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
        tools = [find_games_by_tag]
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