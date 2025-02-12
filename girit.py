import json
import subprocess
import os
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def log_message(message, message_type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{message_type}] {message}")

def run_cmd(args):
    log_message(f"실행할 명령어: {' '.join(args)}", "CMD")
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()

def gather_git_info():
    log_message("Git 저장소 정보 수집 시작")
    info = ""
    info += "=== git status ===\n" + run_cmd(["git", "status"])
    info += "\n=== git diff ===\n" + run_cmd(["git", "diff"])
    info += "\n=== git remote -v ===\n" + run_cmd(["git", "remote", "-v"])
    info += "\n=== 최근 5개 커밋 ===\n" + run_cmd(["git", "log", "--oneline", "-5"])
    log_message("Git 저장소 정보 수집 완료")
    return info

def confirm_execution(command):
    response = input(f"\n실행할 명령어: {command}\n진행하시겠습니까? (y/n): ").lower()
    return response == 'y'

def execute_commands(commands):
    if not isinstance(commands, list):
        commands = [commands]
    
    log_message(f"명령어 실행 시작: {len(commands)}개의 명령어")
    for cmd in commands:
        # git commit 명령을 ai-commit으로 대체
        if cmd.strip() == "git commit" or cmd.strip().startswith("git commit "):
            cmd = "ai-commit"
            log_message("git commit 명령을 ai-commit으로 대체", "INFO")

        log_message(f"명령어 실행 확인 요청: {cmd}", "CONFIRM")
        if confirm_execution(cmd):
            log_message(f"명령어 실행: {cmd}", "EXEC")
            result = os.system(cmd)
            if result != 0:
                log_message(f"명령어 실행 실패 (종료 코드: {result}): {cmd}", "ERROR")
                if input("계속 진행하시겠습니까? (y/n): ").lower() != 'y':
                    log_message("사용자가 실행을 중단함", "CANCEL")
                    return
        else:
            log_message(f"명령어 실행 취소: {cmd}", "CANCEL")
            if input("다음 명령어로 계속 진행하시겠습니까? (y/n): ").lower() != 'y':
                log_message("사용자가 실행을 중단함", "CANCEL")
                return
    log_message("명령어 실행 완료")

def ask_user_choice(options, question):
    log_message(f"사용자 선택 요청: {question}")
    while True:
        # 질문과 옵션을 표시
        print(f"\n? {question}")
        for i, option in enumerate(options, start=1):
            print(f"  {i}) {option}")
        print("  a) 모두 실행")
        
        # 사용자 입력 받기
        choice = input("답변 (숫자 입력, 모두 실행: a, 취소: q): ").lower()
        
        # 취소 처리
        if choice == 'q':
            log_message("사용자가 선택을 취소함", "CANCEL")
            exit(0)
        
        # 모두 실행 처리
        if choice == 'a':
            log_message("모든 옵션 실행 선택")
            return options
        
        # 단일 선택 처리
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(options):
                selected = options[choice_idx]
                log_message(f"사용자 선택: {selected}")
                return [selected]
            else:
                print(f"1부터 {len(options)}까지의 숫자를 입력하세요.")
        except ValueError:
            if choice != 'a':  # 'a'가 아닌 잘못된 입력인 경우에만 에러 메시지
                print("올바른 숫자를 입력하세요.")

def process_message(message):
    log_message("OpenAI 응답 처리 시작")
    fc_list = []
    tool_calls = message.tool_calls
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.type == 'function':
                try:
                    fc_list.append({
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    })
                except Exception as e:
                    log_message(f"함수 호출 처리 중 오류 발생: {str(e)}", "ERROR")
    else:
        content = message.content or ""
        content = content.strip()
        if content.startswith("["):
            try:
                parsed_content = json.loads(content)
                if isinstance(parsed_content, list):
                    for item in parsed_content:
                        if isinstance(item, str):
                            fc_list.append({
                                "name": "execute_commands",
                                "arguments": {"commands": [item]}
                            })
                        else:
                            # functions. 제거
                            if isinstance(item, dict):
                                name = item.get('name', '')
                                if name.startswith('functions.'):
                                    item['name'] = name.replace('functions.', '')
                            fc_list.append(item)
            except Exception as e:
                log_message(f"JSON 파싱 중 오류 발생: {str(e)}", "ERROR")
        elif content:  # 단일 명령어인 경우
            fc_list.append({
                "name": "execute_commands",
                "arguments": {"commands": [content]}
            })
    
    log_message(f"처리된 명령어 목록: {fc_list}")
    log_message("OpenAI 응답 처리 완료")
    return fc_list if fc_list else None

def generate_response(natural_instr, conversation=None):
    log_message("OpenAI API 요청 준비")
    if conversation is None:
        conversation = []
    git_info = gather_git_info()
    conversation.append({
        "role": "user",
        "content": f"현재 repo 상태:\n{git_info}\n{natural_instr}"
    })
    system_msg = (
        "너는 git과 GitHub CLI 전문가야. 현재 path의 repo 정보를 기반으로, "
        "오직 실행 가능한 커맨드만 출력해. 명령의 순서는 너무나 중요해. 명령의 설명은 필요없어. "
        "'git commit' 또는 'git commit -m' 형식의 명령어 대신 'ai-commit'을 사용해. "
        "다수의 펑션콜링이 필요하면 배열 형태로 반환해라.응답은 반드시 다음 형식을 따라야 해\n"
        "[\n"
        '  {\n'
        '    "name": "execute_commands",\n'
        '    "arguments": {"commands": ["git status", "git diff"]}\n'
        "  }\n"
        "]"
    )
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_commands",
                "description": "실행 가능한 git 또는 GitHub CLI 명령어를 실행한다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commands": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["commands"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "ask_user_choice",
                "description": "사용자에게 선택을 요청하고 선택한 명령어를 반환한다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "options": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "question": {"type": "string"}
                    },
                    "required": ["options", "question"]
                }
            }
        }
    ]

    try:
        log_message("OpenAI API 호출")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_msg}] + conversation,
            tools=tools,
            tool_choice="auto"
        )
        log_message("OpenAI API 응답 수신 완료")
        return response
    except Exception as e:
        log_message(f"API 호출 실패: {str(e)}", "ERROR")
        exit(1)

def main():
    log_message("프로그램 시작")
    
    # 기본 명령어를 여기에 설정
    default_instruction = "현재 깃 상태를 확인하고 필요한 작업을 제안해줘"
    log_message(f"기본 명령어: {default_instruction}")
    
    response = generate_response(default_instruction)
    message = response.choices[0].message

    fc_list = process_message(message)
    if fc_list:
        for fc in fc_list:
            name = fc.get("name")
            args = fc.get("arguments", {})
            if name == "execute_commands":
                commands = args.get("commands", [])
                execute_commands(commands)
            elif name == "ask_user_choice":
                options = args.get("options", [])
                question = args.get("question", "선택하세요:")
                selected = ask_user_choice(options, question)
                execute_commands(selected)
    else:
        cmd = message.content.strip() if message.content else ""
        if cmd:
            if confirm_execution(cmd):
                log_message(f"단일 명령어 실행: {cmd}", "EXEC")
                os.system(cmd)
            else:
                log_message(f"단일 명령어 실행 취소: {cmd}", "CANCEL")
        else:
            log_message("실행할 명령어 없음", "INFO")
    
    log_message("프로그램 종료")

if __name__ == "__main__":
    main()