import re
import random

# 定义规则库：模式(正则表达式) -> 响应模板列表
rules = {
    r'I need (.*)': [
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "Are you sure you need {0}?"
    ],
    r'Why don\'t you (.*)\?': [
        "Do you really think I don't {0}?",
        "Perhaps eventually I will {0}.",
        "Do you really want me to {0}?"
    ],
    r'Why can\'t I (.*)\?': [
        "Do you think you should be able to {0}?",
        "If you could {0}, what would you do?",
        "I don't know -- why can't you {0}?"
    ],
    r'I work on (.*)': [
        "What is the most challenging part of working on {0}?",
        "How do you feel about your progress on {0}?",
        "What would success on {0} look like for you?"
    ],
    r'I work as (.*)': [
        "How do you feel about working as {0}?",
        "What do you enjoy most about being {0}?",
        "What is most stressful about being {0}?"
    ],
    r'I am studying (.*)': [
        "What motivated you to study {0}?",
        "Which part of {0} is most difficult right now?",
        "How do you usually learn {0} effectively?"
    ],
    r'I like (.*)': [
        "What do you enjoy most about {0}?",
        "How long have you liked {0}?",
        "What does {0} bring to your life?"
    ],
    r'My hobby is (.*)': [
        "How did you start this hobby: {0}?",
        "What makes {0} meaningful to you?",
        "How often do you spend time on {0}?"
    ],
    r'I am (.*)': [
        "Did you come to me because you are {0}?",
        "How long have you been {0}?",
        "How do you feel about being {0}?"
    ],
    r'.* mother .*': [
        "Tell me more about your mother.",
        "What was your relationship with your mother like?",
        "How do you feel about your mother?"
    ],
    r'.* father .*': [
        "Tell me more about your father.",
        "How did your father make you feel?",
        "What has your father taught you?"
    ],
    r'.*': [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?"
    ]
}

# 定义代词转换规则
pronoun_swap = {
    "i": "you", "you": "i", "me": "you", "my": "your",
    "am": "are", "are": "am", "was": "were", "i'd": "you would",
    "i've": "you have", "i'll": "you will", "yours": "mine",
    "mine": "yours"
}

def swap_pronouns(phrase):
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    words = phrase.lower().split()
    swapped_words = [pronoun_swap.get(word, word) for word in words]
    return " ".join(swapped_words)

def update_memory(user_input, memory):
    name_match = re.search(r'\bmy name is\s+([A-Za-z][A-Za-z\-]*)\b', user_input, re.IGNORECASE)
    if name_match:
        memory["name"] = name_match.group(1)

    age_match = re.search(r'\bi am\s+(\d{1,3})\s+years old\b', user_input, re.IGNORECASE)
    if age_match:
        memory["age"] = age_match.group(1)

    job_match = re.search(r'\bi work as\s+(?:a|an)?\s*(.+)$', user_input, re.IGNORECASE)
    if job_match:
        memory["occupation"] = job_match.group(1).strip().rstrip(".!?")

def respond(user_input, memory):
    """
    根据规则库生成响应
    """
    normalized = user_input.strip().lower()

    if re.search(r'what is my name|do you remember my name', normalized):
        if memory["name"]:
            return f"Your name is {memory['name']}. Did I get it right?"
        return "I don't know your name yet. You can tell me by saying: my name is ..."

    if re.search(r'how old am i|do you remember my age', normalized):
        if memory["age"]:
            return f"You told me you are {memory['age']} years old."
        return "I don't know your age yet. You can tell me by saying: I am ... years old."

    if re.search(r'what is my job|what is my occupation|do you remember my job', normalized):
        if memory["occupation"]:
            return f"You told me you work as {memory['occupation']}."
        return "I don't know your occupation yet. You can tell me by saying: I work as ..."

    for pattern, responses in rules.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            # 捕获匹配到的部分
            captured_group = match.group(1) if match.groups() else ''
            # 进行代词转换
            swapped_group = swap_pronouns(captured_group)
            # 从模板中随机选择一个并格式化
            response = random.choice(responses).format(swapped_group)
            return response
    # 如果没有匹配任何特定规则，使用最后的通配符规则
    return random.choice(rules[r'.*'])

# 主聊天循环
if __name__ == '__main__':
    print("Therapist: Hello! How can I help you today?")
    memory = {"name": None, "age": None, "occupation": None}
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Therapist: Goodbye. It was nice talking to you.")
            break
        update_memory(user_input, memory)
        response = respond(user_input, memory)
        print(f"Therapist: {response}")
