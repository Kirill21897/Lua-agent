from src.agent import LuaAgent

def main():
    agent = LuaAgent()
    print("AI Lua Agent (MVP) запущен. Введите 'exit' для выхода.")
    
    while True:
        user_input = input("\nЗапрос > ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        result = agent.run(user_input)
        if result:
            with open("workspace/final_result.lua", "w") as f:
                f.write(result)
            print("[*] Финальный код сохранен в workspace/final_result.lua")

if __name__ == "__main__":
    main()