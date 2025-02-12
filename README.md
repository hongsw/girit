
# Girit CLI

Girit is a command-line tool that leverages OpenAI's GPT to convert natural language instructions into executable Git commands by analyzing your current repository state.

## Features

- **Repository Analysis:** Automatically gathers Git status, diffs, remotes, and recent commits.
- **Natural Language Interface:** Translates user-provided descriptions into Git commands.
- **Interactive Mode:** Prompts for user selection when multiple command options are available.
- **CLI Packaging:** Installable via pip for easy integration and use as a CLI tool.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd girit
   ```

2. **Install the package:**
   ```bash
   pip install .
   ```

## Configuration

- **OpenAI API Key:**  
  Girit requires an OpenAI API key to function. Set it in your environment:
  ```bash
  export OPENAI_API_KEY=your_api_key_here
  ```

## Usage

Simply run the CLI tool:
```bash
girit
```
Follow the prompt to input your Git command description. Girit will analyze your repository and execute the appropriate Git commands based on your input.

## example

```bash
girit
[2025-02-12 23:17:49] [INFO] 프로그램 시작
[2025-02-12 23:17:49] [INFO] 기본 명령어: 현재 깃 상태를 확인하고 필요한 작업을 제안해줘
[2025-02-12 23:17:49] [INFO] OpenAI API 요청 준비
[2025-02-12 23:17:49] [INFO] Git 저장소 정보 수집 시작
[2025-02-12 23:17:49] [CMD] 실행할 명령어: git status
[2025-02-12 23:17:50] [CMD] 실행할 명령어: git diff
[2025-02-12 23:17:50] [CMD] 실행할 명령어: git remote -v
[2025-02-12 23:17:50] [CMD] 실행할 명령어: git log --oneline -5
[2025-02-12 23:17:50] [INFO] Git 저장소 정보 수집 완료
[2025-02-12 23:17:50] [INFO] OpenAI API 호출
[2025-02-12 23:17:52] [INFO] OpenAI API 응답 수신 완료
[2025-02-12 23:17:52] [INFO] OpenAI 응답 처리 시작
[2025-02-12 23:17:52] [INFO] 처리된 명령어 목록: [{'name': 'execute_commands', 'arguments': {'commands': ['git pull origin main']}}]
[2025-02-12 23:17:52] [INFO] OpenAI 응답 처리 완료
[2025-02-12 23:17:52] [INFO] 명령어 실행 시작: 1개의 명령어
[2025-02-12 23:17:52] [CONFIRM] 명령어 실행 확인 요청: git pull origin main

실행할 명령어: git pull origin main
진행하시겠습니까? (y/n): y 
[2025-02-12 23:17:54] [EXEC] 명령어 실행: git pull origin main
https://github.com/hongsw/girit URL에서
 * branch            main       -> FETCH_HEAD
이미 업데이트 상태입니다.
[2025-02-12 23:17:55] [INFO] 명령어 실행 완료
[2025-02-12 23:17:55] [INFO] 프로그램 종료
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests on GitHub.

## License

This project is licensed under the MIT License.
