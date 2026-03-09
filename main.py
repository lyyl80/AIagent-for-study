from agent.chat_agent import ChatAgent

if __name__ == "__main__":
    print("====MARS Agent====")
    while True:
        user_input = input("You: ")
        agent = ChatAgent(user_input)
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        
        agent.run()
        
