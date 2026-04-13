import subprocess
import os
from config import Config

class LuaTools:
    @staticmethod
    def validate_syntax(code: str) -> tuple[bool, str]:
        """Проверка синтаксиса через luac -p"""
        file_path = os.path.join(Config.WORKSPACE_DIR, "temp.lua")
        with open(file_path, "w") as f:
            f.write(code)
        
        result = subprocess.run(["luac", "-p", file_path], capture_output=True, text=True)
        return result.returncode == 0, result.stderr

    @staticmethod
    def execute(code: str) -> tuple[bool, str]:
        """Выполнение кода в песочнице (subprocess + timeout)"""
        file_path = os.path.join(Config.WORKSPACE_DIR, "temp.lua")
        try:
            result = subprocess.run(
                ["lua", file_path], 
                capture_output=True, 
                text=True, 
                timeout=Config.EXECUTION_TIMEOUT
            )
            return result.returncode == 0, result.stdout if result.returncode == 0 else result.stderr
        except subprocess.TimeoutExpired:
            return False, "Error: Execution timed out (5s limit)"