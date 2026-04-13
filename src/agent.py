import requests
import re
from src.config import Config
from tools import LuaTools
import src.prompts as prompts
import os

class LuaAgent:
    def __init__(self):
        self.config = Config()
        os.makedirs(self.config.WORKSPACE_DIR, exist_ok=True)

    def ask_llm(self, prompt: str) -> str:
        payload = {
            "model": self.config.MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"num_ctx": self.config.CONTEXT_WINDOW, "temperature": 0.2}
        }
        response = requests.post(self.config.OLLAMA_URL, json=payload)
        return response.json().get("response", "")

    def extract_code(self, text: str) -> str:
        code_blocks = re.findall(r"```lua\n(.*?)\n```", text, re.DOTALL)
        return code_blocks[-1] if code_blocks else ""

    def run(self, task: str):
        print(f"[*] Задача: {task}")
        current_prompt = f"{prompts.SYSTEM_PROMPT}\nЗадача: {task}"
        
        for i in range(self.config.MAX_ITERATIONS):
            print(f"[ Итерация {i+1} ]")
            
            # 1. Рассуждение и генерация
            response = self.ask_llm(current_prompt)
            code = self.extract_code(response)
            
            if not code:
                print("[-] Код не найден в ответе LLM.")
                break

            # 2. Валидация
            is_valid, syntax_err = LuaTools.validate_syntax(code)
            if not is_valid:
                print(f"[-] Ошибка синтаксиса: {syntax_err}")
                current_prompt += f"\nObservation: Ошибка синтаксиса: {syntax_err}\n{prompts.FIX_PROMPT.format(error=syntax_err)}"
                continue

            # 3. Выполнение
            success, output = LuaTools.execute(code)
            if success:
                print("[+] Успех!")
                print(f"--- Результат ---\n{output}")
                return code
            else:
                print(f"[-] Ошибка выполнения: {output}")
                current_prompt += f"\nObservation: Ошибка выполнения: {output}\n{prompts.FIX_PROMPT.format(error=output)}"

        return "Не удалось создать рабочий код за лимит итераций."