from src.agent import LuaAgent

def main():
    agent = LuaAgent()
    print("AI Lua Agent (MVP) запущен. Введите 'exit' для выхода.")
    
    while True:
        user_input = input("\nЗапрос > ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        result = agent.run(user_input)
        if isinstance(result, dict):
            if result.get("type") == "success":
                with open("workspace/final_result.lua", "w", encoding="utf-8") as f:
                    f.write(result["content"])
                print("[*] Финальный код сохранен в workspace/final_result.lua")
            elif result.get("type") == "error":
                print(f"[-] Ошибка: {result['content']}")
        elif isinstance(result, str) and result:
            with open("workspace/final_result.lua", "w", encoding="utf-8") as f:
                f.write(result)
            print("[*] Финальный код сохранен в workspace/final_result.lua")

if __name__ == "__main__":
    main()