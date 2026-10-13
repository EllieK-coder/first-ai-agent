# 1. import ollama
# 2. call ollama.chat() with:
#      model = "llama3.2"
#      messages = a list containing ONE dict: role "user", content "Say hi in 5 words"
# 3. store the result in a variable called response
# 4. print(response)

import ollama

response = ollama.chat(
    model="llama3.2",
    messages=[
        {"role": "user", "content": "Say hi in 5 words"}

    ]
)

print(response.message.content)
