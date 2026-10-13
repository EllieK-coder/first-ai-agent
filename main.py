import ollama

messages = []          # an empty list

while True:
    user_text = input("You: ")

    if user_text == "quit":
        break

    messages.append({"role": "user", "content": user_text})

    response = ollama.chat(model="llama3.2", messages=messages)
    reply = response.message.content

    print("AI:", reply)

    messages.append({"role": "assistant", "content": reply})


    def get_my_games() -> str:
        """Get the list of games the user owns, with their tags and hours played."""
        games = [
            {"name": "Hades", "tags": ["action", "roguelike"], "hours": 40},
            {"name": "Stardew Valley", "tags": ["cozy", "farming"], "hours": 120},
            # add 3 more of your own games here
        ]
        return str(games)