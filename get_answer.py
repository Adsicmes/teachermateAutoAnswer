import json
import subprocess
import settings
from openai import OpenAI
from openai.types.chat import ChatCompletion

openai_client = OpenAI(api_key=settings.gpt_api_key)

question_file = "paper-662477.json"

data = json.load(open(question_file, "r", encoding="utf-8"))

questions = []

for k, v in data.items():
    questions += v

print(len(questions))
print("\n\n\n================================")


# 1单选 2多选
index = 1
for q in questions:
    match q["type"]:
        case 1:
            content = (f"该题是单选题\n"
                       f"{q['content']}\n"
                       f"\n")
            content += "\n".join(i["content"] for i in q["answerContent"])
        case 2:
            content = (f"该题是多选题\n"
                       f"{q['content']}\n"
                       f"\n")
            content += "\n".join(i["content"] for i in q["answerContent"])
        case _:
            content = ""
    result: ChatCompletion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "接下来我会给你一道题目，请使用尽量简短的语言告诉我答案，无需任何解释或多余的描述。"
                           "如果本题是选择选项的题，直接说出选项的内容，不要出现选项之外的文字，不要使用\"第几个选项\"类似的语句或使用ABCD之类的字母来表示选项。"
                           "尽量使用markdown格式的无序列表告诉我答案。"
                           "如果是单选题，请直接告诉我答案选项的内容，不要使用\"正确答案\"之类的字眼。"
                           "如果是多选题，请用换行隔开选项内容。"
                           "\n\n题目：\n"
                           f"{content}\n",
            }
        ],
    )
    print(index)
    print(result.choices[0].message.content)
    with open(f"answer-{question_file}.txt", "a", encoding="utf-8") as f:
        f.write(f"{result.choices[0].message.content.replace('-', '').strip()}\n")
    print("====================================")
    index += 1
