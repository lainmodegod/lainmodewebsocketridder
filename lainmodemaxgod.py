#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     ██╗      █████╗ ██╗███╗   ██╗███╗   ███╗ ██████╗ ██████╗ ███████╗     ║
║     ██║     ██╔══██╗██║████╗  ██║████╗ ████║██╔═══██╗██╔══██╗██╔════╝     ║
║     ██║     ███████║██║██╔██╗ ██║██╔████╔██║██║   ██║██║  ██║█████╗       ║
║     ██║     ██╔══██║██║██║╚██╗██║██║╚██╔╝██║██║   ██║██║  ██║██╔══╝       ║
║     ███████╗██║  ██║██║██║ ╚████║██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗     ║
║     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝     ║
║                                                                            ║
║                    ██╗    ██╗███████╗██████╗ ███████╗ ██████╗              ║
║                    ██║    ██║██╔════╝██╔══██╗██╔════╝██╔═══██╗             ║
║                    ██║ █╗ ██║█████╗  ██████╔╝███████╗██║   ██║             ║
║                    ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║   ██║             ║
║                    ╚███╔███╔╝███████╗██████╔╝███████║╚██████╔╝             ║
║                     ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝ ╚═════╝              ║
║                                                                            ║
║              🔥 Universal WebSocket Security Testing Tool 🔥               ║
║                                                                            ║
║                    Created with 💜 by lainmode                             ║
║                         Version 1.0.0 - "Riddler"                          ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

                            ⭐ DON'T FORGET TO STAR! ⭐
"""

import websocket
import json
import time
import ssl
import sys
import os
import yaml
import argparse
import signal
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from pathlib import Path
import random

# ==============================================================================
#                            ЦВЕТА ДЛЯ КРАСИВОГО ВЫВОДА
# ==============================================================================

class Colors:
    """🎨 Цветная магия для твоего терминала"""
    
    # Основные цвета
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Стили
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Фоны
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # Сброс
    END = '\033[0m'
    
    # Иконки
    ICON_SUCCESS = "✅"
    ICON_ERROR = "❌"
    ICON_WARNING = "⚠️"
    ICON_INFO = "ℹ️"
    ICON_CRITICAL = "🚨"
    ICON_BUG = "🐛"
    ICON_LOCK = "🔒"
    ICON_UNLOCK = "🔓"
    ICON_KEY = "🔑"
    ICON_SKULL = "💀"
    ICON_FIRE = "🔥"
    ICON_STAR = "⭐"
    ICON_HEART = "💜"
    ICON_ROCKET = "🚀"
    ICON_MAGIC = "✨"
    ICON_BOMB = "💣"
    ICON_EYE = "👁️"
    ICON_TARGET = "🎯"
    
    @classmethod
    def success(cls, text):
        return f"{cls.GREEN}{cls.ICON_SUCCESS} {text}{cls.END}"
    
    @classmethod
    def error(cls, text):
        return f"{cls.RED}{cls.ICON_ERROR} {text}{cls.END}"
    
    @classmethod
    def warning(cls, text):
        return f"{cls.YELLOW}{cls.ICON_WARNING} {text}{cls.END}"
    
    @classmethod
    def info(cls, text):
        return f"{cls.BLUE}{cls.ICON_INFO} {text}{cls.END}"
    
    @classmethod
    def critical(cls, text):
        return f"{cls.RED}{cls.BOLD}{cls.ICON_CRITICAL} {text}{cls.END}"
    
    @classmethod
    def highlight(cls, text):
        return f"{cls.CYAN}{cls.BOLD}{text}{cls.END}"
    
    @classmethod
    def header(cls, text):
        return f"{cls.MAGENTA}{cls.BOLD}╔══ {text} ══╗{cls.END}"
    
    @classmethod
    def subheader(cls, text):
        return f"{cls.CYAN}║ {text}{cls.END}"
    
    @classmethod
    def progress(cls, current, total, text=""):
        percentage = (current / total) * 100
        bar_length = 30
        filled = int(bar_length * current // total)
        bar = '█' * filled + '░' * (bar_length - filled)
        return f"{cls.YELLOW}{bar} {percentage:.1f}% {text}{cls.END}"

# ==============================================================================
#                             КОНФИГУРАЦИЯ
# ==============================================================================

@dataclass
class TargetConfig:
    """🎯 Конфигурация целей для тестирования"""
    chats: List[int] = field(default_factory=list)
    users: List[int] = field(default_factory=list)
    messages: List[int] = field(default_factory=list)
    custom: Dict[str, List[int]] = field(default_factory=dict)

@dataclass
class TestConfig:
    """⚙️ Основная конфигурация тестирования"""
    
    # Подключение
    url: str = "wss://example.com/websocket"
    token: str = ""
    proxy: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=lambda: {
        "Origin": "https://example.com",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    })
    
    # Цели
    targets: TargetConfig = field(default_factory=TargetConfig)
    
    # Сообщения
    init_message: Dict[str, Any] = field(default_factory=lambda: {
        "ver": 11,
        "cmd": 0,
        "opcode": 19,
        "payload": {
            "interactive": True,
            "token": "{token}"
        }
    })
    
    test_messages: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            "opcode": 79,
            "payload": {"chatIds": ["{target}"]},
            "name": "chat_history",
            "type": "chat",
            "validator": "history in response"
        },
        {
            "opcode": 48,
            "payload": {"userId": ["{target}"]},
            "name": "user_profile",
            "type": "user",
            "validator": "profile in response"
        }
    ])
    
    # Настройки
    delay_between_tests: float = 1.0
    delay_after_init: float = 0.5
    max_workers: int = 3
    save_responses: bool = True
    verbose: bool = False
    output_dir: str = "results"
    
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    ])

# ==============================================================================
#                          ОСНОВНОЙ КЛАСС ТЕСТЕРА
# ==============================================================================

class LainModeWebSocketRiddler:
    """
    🕵️ Главный класс для тестирования WebSocket API
    
    Создан lainmode для всех баг-хантеров мира 🌍
    """
    
    def __init__(self, config: TestConfig):
        """
        Инициализация тестера
        
        Args:
            config: Конфигурация тестирования
        """
        self.config = config
        self.results = {
            "metadata": {
                "start_time": datetime.now().isoformat(),
                "url": config.url,
                "targets": asdict(config.targets),
            },
            "vulnerabilities": [],
            "secured": [],
            "errors": [],
            "responses": {}
        }
        self._setup_output_dir()
        self._print_welcome()
    
    def _setup_output_dir(self):
        """📁 Создает папку для результатов"""
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _print_welcome(self):
        """👋 Приветственное сообщение"""
        print(f"\n{Colors.BG_BLACK}{Colors.BOLD}{Colors.GREEN}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + " " * 20 + Colors.YELLOW + "🔥 LAINMODE WEBSOCKET RIDDLER ACTIVATED 🔥" + Colors.GREEN + " " * 19 + "║")
        print("║" + " " * 78 + "║")
        print("║" + " " * 10 + Colors.CYAN + "Ready to crack some WebSockets!" + Colors.GREEN + " " * 26 + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print(Colors.END)
        
        print(f"\n{Colors.info(f'Target URL: {Colors.BOLD}{self.config.url}{Colors.END}')}")
        print(f"{Colors.info(f'Token: {Colors.BOLD}{self.config.token[:20]}...{Colors.END}')}")
        
        total_targets = (
            len(self.config.targets.chats) +
            len(self.config.targets.users) +
            len(self.config.targets.messages)
        )
        print(f"{Colors.info(f'Total targets: {Colors.BOLD}{total_targets}{Colors.END}')}")
        print(f"{Colors.info(f'Test messages: {Colors.BOLD}{len(self.config.test_messages)}{Colors.END}')}")
        print()
    
    def create_connection(self, user_agent: str = None) -> Optional[websocket.WebSocket]:
        """
        🔌 Создает WebSocket соединение
        
        Args:
            user_agent: User-Agent для запроса
            
        Returns:
            WebSocket объект или None
        """
        if not user_agent:
            user_agent = random.choice(self.config.user_agents)
        
        headers = {
            "User-Agent": user_agent,
            **self.config.headers
        }
        
        try:
            ws = websocket.WebSocket()
            
            if self.config.proxy:
                from urllib.parse import urlparse
                p = urlparse(self.config.proxy)
                ws.connect(
                    self.config.url,
                    http_proxy_host=p.hostname,
                    http_proxy_port=p.port,
                    header=headers,
                    sslopt={"cert_reqs": ssl.CERT_NONE}
                )
                if self.config.verbose:
                    print(f"{Colors.info(f'Connected via proxy {p.hostname}:{p.port}')}")
            else:
                ws.connect(
                    self.config.url,
                    header=headers,
                    sslopt={"cert_reqs": ssl.CERT_NONE}
                )
            
            if self.config.verbose:
                print(f"{Colors.success(f'Connection established with {user_agent[:30]}...')}")
            
            return ws
            
        except Exception as e:
            print(f"{Colors.error(f'Connection failed: {e}')}")
            return None
    
    def send_message(self, ws: websocket.WebSocket, message: Dict) -> Optional[Dict]:
        """
        📤 Отправляет сообщение и получает ответ
        
        Args:
            ws: WebSocket соединение
            message: Сообщение для отправки
            
        Returns:
            Ответ сервера или None
        """
        try:
            msg_str = json.dumps(message, ensure_ascii=False)
            if self.config.verbose:
                print(f"{Colors.info(f'Sending: {msg_str[:100]}...')}")
            
            ws.send(msg_str)
            response = ws.recv()
            
            try:
                return json.loads(response)
            except:
                return {"raw": response[:200]}
                
        except Exception as e:
            print(f"{Colors.error(f'Send failed: {e}')}")
            return None
    
    def initialize(self, ws: websocket.WebSocket) -> bool:
        """
        🔑 Инициализация сессии с токеном
        
        Args:
            ws: WebSocket соединение
            
        Returns:
            True если успешно
        """
        # Подставляем токен в сообщение
        init_str = json.dumps(self.config.init_message)
        init_str = init_str.replace("{token}", self.config.token)
        init_msg = json.loads(init_str)
        
        response = self.send_message(ws, init_msg)
        
        if not response:
            return False
        
        if "payload" in response:
            if "error" not in response["payload"]:
                if self.config.verbose:
                    print(f"{Colors.success('Initialization successful')}")
                return True
            else:
                error = response["payload"]["error"]
                print(f"{Colors.warning(f'Init error: {error}')}")
                return False
        
        return False
    
    def analyze_response(self, response: Dict, target: int, target_type: str, test_name: str) -> Tuple[bool, str]:
        """
        🔍 Анализирует ответ на наличие уязвимости
        
        Args:
            response: Ответ сервера
            target: ID цели
            target_type: Тип цели (chat/user/message)
            test_name: Название теста
            
        Returns:
            (is_vulnerable, reason)
        """
        if not response:
            return False, "No response"
        
        # Проверяем на наличие данных
        if "payload" in response:
            payload = response["payload"]
            
            # Если есть история - это данные чата
            if "history" in payload:
                history = payload.get("history", [])
                if history:
                    return True, f"Found {len(history)} messages"
            
            # Если есть профиль - данные пользователя
            if "profile" in payload or "contact" in payload:
                return True, "Found user profile"
            
            # Если есть чаты - список чатов
            if "chats" in payload:
                chats = payload.get("chats", [])
                if chats:
                    return True, f"Found {len(chats)} chats"
            
            # Если ошибка доступа - защищено
            if "error" in payload:
                error = payload["error"]
                if error == "access denied":
                    return False, "Access denied"
                return False, f"Error: {error}"
        
        return False, "No sensitive data"
    
    def test_target(self, target: int, target_type: str, test_config: Dict) -> Dict:
        """
        🎯 Тестирует одну цель
        
        Args:
            target: ID цели
            target_type: Тип цели
            test_config: Конфигурация теста
            
        Returns:
            Результат теста
        """
        result = {
            "target": target,
            "type": target_type,
            "test_name": test_config.get("name", "unknown"),
            "opcode": test_config.get("opcode"),
            "timestamp": datetime.now().isoformat(),
            "vulnerable": False,
            "reason": "",
            "response": None
        }
        
        if self.config.verbose:
            print(f"\n{Colors.highlight(f'Testing {target_type} {target} with opcode {test_config["opcode"]}...')}")
        
        # Создаем соединение
        ws = self.create_connection()
        if not ws:
            result["reason"] = "Connection failed"
            return result
        
        try:
            # Инициализация
            if not self.initialize(ws):
                result["reason"] = "Initialization failed"
                ws.close()
                return result
            
            time.sleep(self.config.delay_after_init)
            
            # Формируем тестовое сообщение
            test_str = json.dumps(test_config["payload"])
            test_str = test_str.replace("{target}", str(target))
            test_msg = json.loads(test_str)
            test_msg["ver"] = 11
            test_msg["cmd"] = 0
            test_msg["seq"] = 2
            test_msg["opcode"] = test_config["opcode"]
            
            # Отправляем
            response = self.send_message(ws, test_msg)
            
            if response:
                result["response"] = response
                
                # Анализируем
                vulnerable, reason = self.analyze_response(response, target, target_type, test_config["name"])
                result["vulnerable"] = vulnerable
                result["reason"] = reason
                
                if vulnerable:
                    print(f"{Colors.critical(f'🚨 VULNERABILITY FOUND! {target_type} {target} - {reason}')}")
                elif self.config.verbose:
                    print(f"{Colors.success(f'Secured: {reason}')}")
            
            ws.close()
            
        except Exception as e:
            result["reason"] = f"Error: {e}"
            print(f"{Colors.error(f'Test failed: {e}')}")
            try:
                ws.close()
            except:
                pass
        
        return result
    
    def run(self) -> Dict:
        """
        ▶️ Запускает тестирование всех целей
        
        Returns:
            Результаты всех тестов
        """
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{Colors.ICON_ROCKET} STARTING TESTS {Colors.ICON_ROCKET}{Colors.END}\n")
        
        all_tests = []
        
        # Собираем все тесты
        for test in self.config.test_messages:
            target_type = test.get("type", "unknown")
            
            if target_type == "chat":
                targets = self.config.targets.chats
            elif target_type == "user":
                targets = self.config.targets.users
            elif target_type == "message":
                targets = self.config.targets.messages
            else:
                targets = self.config.targets.custom.get(target_type, [])
            
            for target in targets:
                all_tests.append((target, target_type, test))
        
        total = len(all_tests)
        
        # Запускаем тесты
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            for target, target_type, test in all_tests:
                future = executor.submit(self.test_target, target, target_type, test)
                futures.append(future)
                time.sleep(self.config.delay_between_tests)
            
            # Собираем результаты
            for i, future in enumerate(as_completed(futures), 1):
                result = future.result()
                
                if result["vulnerable"]:
                    self.results["vulnerabilities"].append(result)
                elif result["reason"] and "denied" in result["reason"]:
                    self.results["secured"].append(result)
                else:
                    self.results["errors"].append(result)
                
                # Прогресс
                print(f"\r{Colors.progress(i, total, f'{i}/{total} tests')}", end="")
        
        print(f"\n\n{Colors.success(f'Testing completed!')}")
        
        # Сохраняем результаты
        self._save_results()
        
        return self.results
    
    def _save_results(self):
        """💾 Сохраняет результаты в файлы"""
        timestamp = int(time.time())
        
        # Основной JSON
        json_file = f"{self.config.output_dir}/results_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Markdown отчет
        md_file = f"{self.config.output_dir}/report_{timestamp}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(self._generate_markdown_report())
        
        # Текстовый summary
        txt_file = f"{self.config.output_dir}/summary_{timestamp}.txt"
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(self._generate_text_summary())
        
        print(f"\n{Colors.success(f'Results saved:')}")
        print(f"  {Colors.info(f'JSON: {json_file}')}")
        print(f"  {Colors.info(f'Markdown: {md_file}')}")
        print(f"  {Colors.info(f'Summary: {txt_file}')}")
    
    def _generate_markdown_report(self) -> str:
        """📝 Генерирует Markdown отчет"""
        report = []
        report.append(f"# 🔥 LainMode WebSocket Riddler Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Target URL:** `{self.config.url}`\n")
        report.append(f"## 📊 Statistics\n")
        report.append(f"- Total tests: {len(self.results['vulnerabilities']) + len(self.results['secured']) + len(self.results['errors'])}")
        report.append(f"- 🔴 Vulnerabilities: **{len(self.results['vulnerabilities'])}**")
        report.append(f"- 🟢 Secured: {len(self.results['secured'])}")
        report.append(f"- ⚠️ Errors: {len(self.results['errors'])}\n")
        
        if self.results['vulnerabilities']:
            report.append(f"## 🚨 Vulnerabilities Found\n")
            for v in self.results['vulnerabilities']:
                report.append(f"### {v['type']} {v['target']}")
                report.append(f"- **Test:** {v['test_name']} (opcode {v['opcode']})")
                report.append(f"- **Reason:** {v['reason']}")
                report.append(f"- **Time:** {v['timestamp']}\n")
        
        return "\n".join(report)
    
    def _generate_text_summary(self) -> str:
        """📄 Генерирует текстовое резюме"""
        lines = []
        lines.append("=" * 60)
        lines.append("LAINMODE WEBSOCKET RIDDLER - TEST SUMMARY")
        lines.append("=" * 60)
        lines.append(f"\nTarget: {self.config.url}")
        lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\nRESULTS:")
        lines.append(f"  Vulnerabilities: {len(self.results['vulnerabilities'])}")
        lines.append(f"  Secured: {len(self.results['secured'])}")
        lines.append(f"  Errors: {len(self.results['errors'])}")
        
        if self.results['vulnerabilities']:
            lines.append(f"\nVULNERABLE TARGETS:")
            for v in self.results['vulnerabilities']:
                lines.append(f"  • {v['type']} {v['target']} - {v['reason']}")
        
        return "\n".join(lines)
    
    def print_summary(self):
        """📊 Выводит сводку в консоль"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}📊 TEST SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'=' * 60}{Colors.END}")
        
        total = len(self.results['vulnerabilities']) + len(self.results['secured']) + len(self.results['errors'])
        print(f"\n{Colors.info(f'Total tests: {total}')}")
        print(f"{Colors.critical(f'Vulnerabilities: {len(self.results["vulnerabilities"])}')}")
        print(f"{Colors.success(f'Secured: {len(self.results["secured"])}')}")
        print(f"{Colors.warning(f'Errors: {len(self.results["errors"])}')}")
        
        if self.results['vulnerabilities']:
            print(f"\n{Colors.critical('🚨 VULNERABLE TARGETS:')}")
            for v in self.results['vulnerabilities']:
                print(f"  {Colors.critical(f'• {v["type"]} {v["target"]}')} - {v['reason']}")

# ==============================================================================
#                          ЗАГРУЗКА КОНФИГУРАЦИИ
# ==============================================================================

def load_config_from_file(config_file: str) -> TestConfig:
    """
    📂 Загружает конфигурацию из YAML файла
    
    Args:
        config_file: Путь к файлу конфигурации
        
    Returns:
        Объект TestConfig
    """
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    targets = TargetConfig(
        chats=data.get('targets', {}).get('chats', []),
        users=data.get('targets', {}).get('users', []),
        messages=data.get('targets', {}).get('messages', []),
        custom=data.get('targets', {}).get('custom', {})
    )
    
    return TestConfig(
        url=data.get('url', ''),
        token=data.get('token', ''),
        proxy=data.get('proxy'),
        headers=data.get('headers', {}),
        targets=targets,
        init_message=data.get('init_message', {}),
        test_messages=data.get('test_messages', []),
        delay_between_tests=data.get('delay_between_tests', 1.0),
        delay_after_init=data.get('delay_after_init', 0.5),
        max_workers=data.get('max_workers', 3),
        save_responses=data.get('save_responses', True),
        verbose=data.get('verbose', False),
        output_dir=data.get('output_dir', 'results'),
        user_agents=data.get('user_agents', [])
    )

def create_default_config() -> TestConfig:
    """
    📝 Создает конфигурацию по умолчанию
    
    Returns:
        Объект TestConfig с примерными значениями
    """
    return TestConfig(
        url="wss://example.com/websocket",
        token="YOUR_TOKEN_HERE",
        targets=TargetConfig(
            chats=[1001, 1002, 1003],
            users=[2001, 2002, 2003],
            messages=[3001, 3002, 3003]
        ),
        test_messages=[
            {
                "opcode": 79,
                "payload": {"chatIds": ["{target}"]},
                "name": "chat_history",
                "type": "chat",
                "validator": "history in response"
            },
            {
                "opcode": 48,
                "payload": {"userId": "{target}"},
                "name": "user_profile",
                "type": "user",
                "validator": "profile in response"
            }
        ]
    )

# ==============================================================================
#                          КОМАНДНАЯ СТРОКА
# ==============================================================================

def main():
    """🎮 Главная функция для запуска из командной строки"""
    
    parser = argparse.ArgumentParser(
        description="🔥 LainMode WebSocket Riddler - Universal WebSocket Security Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lainmodewebsocketridder.py -u wss://api.example.com/ws -t "token123" -c chats.txt
  python3 lainmodewebsocketridder.py -c config.yaml
  python3 lainmodewebsocketridder.py --generate-config > my_config.yaml
        """
    )
    
    parser.add_argument("-u", "--url", help="WebSocket URL")
    parser.add_argument("-t", "--token", help="Authentication token")
    parser.add_argument("-c", "--config", help="Config file (YAML)")
    parser.add_argument("--generate-config", action="store_true", help="Generate default config")
    parser.add_argument("--chats", help="File with chat IDs (one per line)")
    parser.add_argument("--users", help="File with user IDs (one per line)")
    parser.add_argument("--output", "-o", default="results", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--workers", "-w", type=int, default=3, help="Max workers")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between tests")
    parser.add_argument("--no-color", action="store_true", help="Disable colors")
    
    args = parser.parse_args()
    
    # Отключаем цвета если нужно
    if args.no_color:
        Colors.END = Colors.GREEN = Colors.RED = Colors.YELLOW = Colors.BLUE = Colors.MAGENTA = Colors.CYAN = ""
        Colors.BOLD = ""
    
    # Генерация конфига
    if args.generate_config:
        config = create_default_config()
        print(yaml.dump(asdict(config), default_flow_style=False, allow_unicode=True))
        return
    
    # Загрузка конфига
    if args.config:
        config = load_config_from_file(args.config)
    else:
        if not args.url or not args.token:
            parser.error("URL and token required without config file")
        
        # Загрузка ID из файлов
        chats = []
        if args.chats:
            with open(args.chats, 'r') as f:
                chats = [int(line.strip()) for line in f if line.strip()]
        
        users = []
        if args.users:
            with open(args.users, 'r') as f:
                users = [int(line.strip()) for line in f if line.strip()]
        
        config = TestConfig(
            url=args.url,
            token=args.token,
            targets=TargetConfig(chats=chats, users=users),
            max_workers=args.workers,
            delay_between_tests=args.delay,
            verbose=args.verbose,
            output_dir=args.output
        )
    
    # Запуск тестирования
    riddler = LainModeWebSocketRiddler(config)
    results = riddler.run()
    riddler.print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.warning('Interrupted by user')}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.error(f'Fatal error: {e}')}")
        sys.exit(1)
