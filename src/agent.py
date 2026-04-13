import requests
import re
from src.config import Config
from src.tools import LuaTools
import src.prompts as prompts
import os

class LuaAgent:
    def __init__(self):
        self.config = Config()
        os.makedirs(self.config.WORKSPACE_DIR, exist_ok=True)
        self.history = [{"role": "system", "content": prompts.SYSTEM_PROMPT}]

    def ask_llm(self):
        payload = {
            "model": self.config.MODEL_NAME,
            "messages": self.history,
            "stream": False,
            "options": {
                "num_ctx": self.config.CONTEXT_WINDOW, 
                "temperature": 0.2,
                "num_predict": self.config.NUM_PREDICT,
                "num_batch": self.config.NUM_BATCH,
            }
        }
        
        try:
            response = requests.post(self.config.OLLAMA_URL, json=payload)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            return f"Error communicating with LLM: {str(e)}"

    def extract_code(self, text: str) -> str:
        code_blocks = re.findall(r"```lua\n(.*?)\n```", text, re.DOTALL)
        return code_blocks[-1] if code_blocks else ""

    def run(self, task: str):
        print(f"[*] Пользователь: {task}")
        self.history.append({"role": "user", "content": f"Task: {task}"})
        
        for i in range(self.config.MAX_ITERATIONS):
            print(f"[ Итерация {i+1} ]")
            
            # 1. Рассуждение и генерация
            response = self.ask_llm()
            self.history.append({"role": "assistant", "content": response})
            
            # Проверка на уточняющий вопрос
            question_match = re.search(r"Question:\s*(.+)", response, re.IGNORECASE)
            code = self.extract_code(response)
            
            if question_match and not code:
                # Агент задает вопрос
                question = question_match.group(1).strip()
                print(f"[?] Уточнение от AI: {question}")
                return {"type": "question", "content": question}

            if not code:
                if "Error communicating with LLM" in response:
                    print(response)
                    return {"type": "error", "content": response}
                print(f"[DEBUG RAW RESPONSE]:\n{response}\n---")
                print("[-] Код не найден в ответе LLM, прошу повторить.")
                self.history.append({"role": "user", "content": "Observation: Отсутствует код. Пожалуйста, либо задай уточняющий вопрос через формат `Question: <вопрос>`, либо напиши код в ```lua ... ``` блоке."})
                continue

            # 2. Валидация
            is_valid, syntax_err = LuaTools.validate_syntax(code)
            if not is_valid:
                print(f"[-] Ошибка синтаксиса: {syntax_err}")
                self.history.append({"role": "user", "content": f"Observation: Ошибка синтаксиса: {syntax_err}\n{prompts.FIX_PROMPT.format(error=syntax_err)}"})
                continue

            # 3. Выполнение
            success, output = LuaTools.execute(code)
            if success:
                print("[+] Успех!")
                print(f"--- Результат ---\n{output}")
                return {"type": "success", "content": code}
            else:
                print(f"[-] Ошибка выполнения: {output}")
                self.history.append({"role": "user", "content": f"Observation: Ошибка выполнения: {output}\n{prompts.FIX_PROMPT.format(error=output)}"})

        return {"type": "error", "content": "Не удалось создать рабочий код за лимит итераций."}