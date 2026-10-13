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