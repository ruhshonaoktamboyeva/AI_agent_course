# from google import genai
# from dotenv import load_dotenv


# load_dotenv('.env')

# client = genai.Client()

# while True:
#     k=input('User:  ')
#     if k.lower()=='exit' or k.lower()=='quit':
#         break


#     response = client.models.generate_content(
#         model= "gemini-2.5-flash",
#         contents=k
#     )
#     print("AI:  ", response.text)


from google import genai
from dotenv import load_dotenv

load_dotenv('.env')

client = genai.Client()

# history faylini o‘qiymiz
with open("history.txt", "r", encoding="utf-8") as f:
    history = f.read()



while True:
    k = input('User:  ')
    if k.lower() == 'exit' or k.lower() == 'quit':
        break


    prompt = history + "\nUser: " + k

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print("AI:  ", response.text)


    history += f"\nUser: {k}\nAI: {response.text}"


with open("history.txt", "w", encoding="utf-8") as f:
    f.write(history)

