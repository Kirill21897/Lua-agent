# AI Lua Agent (MVP)

Локальный AI-агент для генерации и отладки Lua-кода, работающий на потребительском железе (8GB VRAM). 
Архитектура ReAct (Reasoning + Acting) с self-healing механизмом.

## Ключевые принципы

1. **Локальность** — никаких API-ключей, работа полностью offline через Ollama
2. **Безопасность** — код выполняется в sandbox с ограничениями по времени/памяти
3. **Итеративность** — агент сам исправляет ошибки (validate → execute → fix loop)

## Архитектура

### C4 Level 1: System Context
```mermaid
flowchart TB
    User([Разработчик]) -->|CLI запрос| Agent[AI Lua Agent]
    Agent -->|HTTP| Ollama[Ollama LLM<br/>Qwen2.5-Coder-7B]
    Agent -->|subprocess| Lua[Lua VM<br/>luac + lua]
    Agent -->|read/write| FS[(Файловая система<br/>workspace/)]
    
    style Agent fill:#ffb6c1,stroke:#333,stroke-width:3px
    style Ollama fill:#c4e0ff,stroke:#333,stroke-width:2px
    style Lua fill:#fff3cd,stroke:#333,stroke-width:2px
```

### C4 Level 2: Container Diagram (Layers)
```mermaid
flowchart TB
    subgraph Input["Input Layer"]
        CLI[CLI Interface<br/>REPL / Single shot]
    end
    
    subgraph Control["Control Layer"]
        React[ReAct Loop<br/>Reasoning + Acting]
        Planner[Task Planner<br/>Simple sequencer]
        Memory[Context Manager<br/>Sliding Window 4K]
    end
    
    subgraph Intelligence["Intelligence Layer"]
        Prompt[Prompt Builder]
        LLM[Ollama Client<br/>7B-Q4 ~4.5GB VRAM]
        Parser[Code Parser<br/>Markdown extractor]
    end
    
    subgraph Tools["Tool Layer"]
        Gen[Tool: generate]
        Val[Tool: validate<br/>luac -p]
        Exec[Tool: execute<br/>sandbox]
        Fix[Tool: fix<br/>error correction]
    end
    
    subgraph Safety["Safety Layer"]
        Guard[ResourceGuard<br/>timeout 5s]
        Temp[TempFS<br/>/tmp/lua_agent]
        VM[Lua Runtime]
    end
    
    subgraph Storage["Storage Layer"]
        Session[Session History<br/>JSON]
        Cache[Prompt Cache<br/>3 turns]
        WS[Workspace<br/>*.lua files]
    end
    
    CLI --> React
    React --> Planner
    Planner --> Memory
    React --> Prompt
    Prompt --> LLM
    LLM --> Parser
    Parser --> Gen
    Gen --> Val
    Val -->|OK| Exec
    Val -->|Error| Fix
    Fix -.-> Gen
    Exec --> Guard
    Guard --> Temp
    Temp --> VM
    Memory --> Cache
    React --> Session
    Exec --> WS
    
    style Control fill:#ffe6f0,stroke:#d63384,stroke-width:3px
    style Intelligence fill:#e6f2ff,stroke:#0d6efd,stroke-width:3px
    style Tools fill:#fff8e1,stroke:#ffc107,stroke-width:3px
    style Safety fill:#ffebee,stroke:#dc3545,stroke-width:3px
    style Storage fill:#e8f5e9,stroke:#198754,stroke-width:3px
```

### Поток данных (ReAct Loop)
```mermaid
sequenceDiagram
    participant U as User
    participant A as Agent Core
    participant L as LLM
    participant T as Tools
    participant S as Sandbox
    
    U->>A: Задача: "сортировка quicksort"
    
    loop Max 3 iterations
        A->>A: Thought: Нужно сгенерировать код
        
        A->>L: Action: generate(prompt)
        L-->>A: Observation: Lua code
        
        A->>T: Action: validate(code)
        T->>S: luac -p
        S-->>T: syntax OK / Error
        
        alt Syntax Error
            A->>L: Action: fix(code, error)
            L-->>A: Observation: fixed code
        else Syntax OK
            A->>T: Action: execute(code)
            T->>S: lua script.lua (timeout 5s)
            S-->>T: output / runtime error
            
            alt Runtime Error
                A->>L: Action: fix(code, stderr)
                L-->>A: Observation: fixed code
            else Success
                A->>U: Final Answer: code + output
            end
        end
    end
```

## Компоненты (план реализации)

| Компонент | Файл | Ответственность | Интерфейс |
|-----------|------|-----------------|-----------|
| **CLI** | `main.py` | argparse, REPL loop, команды (:save, :quit) | `run(), interactive()` |
| **Agent Core** | `agent.py` | ReAct loop, история сессий, оркестрация инструментов | `process(task) -> Result` |
| **Tool Registry** | `tools.py` | Генерация, валидация, исполнение, фикс | `generate(), validate(), execute(), fix()` |
| **Prompts** | `prompts.py` | Системные промпты, шаблоны Jinja2 | константы + format() |
| **Config** | `config.py` | Константы (VRAM, timeouts, paths) | dataclass/settings |

## Ограничения MVP

- **LLM**: Только локальные модели до 7B (Q4), контекст 4K токенов
- **Lua**: Только стандартная библиотека 5.4, один файл на задачу
- **Безопасность**: Песочница только через subprocess + timeout (без полной изоляции контейнера)
- **Память**: Максимум 3 предыдущих обмена в контексте (sliding window)
