from langchain_aws import ChatBedrock

def call_llm(prompt: str, model="mistral.mistral-large-2402-v1:0", temperature=0.7) -> str:
    llm = ChatBedrock(
        model_id=model,
        model_kwargs=dict(temperature=temperature),
        # other params...
    )

    messages = [
        (
            "system",
            "You are a helpful assistant",
        ),
        ("human", prompt),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg

if __name__ == "__main__":
    prompt = "Who are you? What is your purpose?"
    response = call_llm(prompt)
    print(response)
