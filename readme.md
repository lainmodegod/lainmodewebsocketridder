# 🔥 LainMode WebSocket Riddler

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
![Made with 💜](https://img.shields.io/badge/made%20with-%20%F0%9F%92%9C%20by%20lainmode-ff69b4)

> 🕷️ **Universal WebSocket Security Testing Tool** - потому что безопасность должна быть доступной

<img src="https://raw.githubusercontent.com/lainmodegod/lainmodewebsocketridder/main/logo.png" width="200" alt="Logo">

## ✨ Возможности

- 🎯 **IDOR Hunting** - автоматический поиск уязвимостей доступа
- 🔌 **Universal** - работает с любым WebSocket API
- ⚡ **Fast** - асинхронные запросы, параллельное тестирование
- 📊 **Reports** - красивые отчеты в JSON, Markdown, TXT
- 🎨 **Beautiful UI** - цветной вывод, прогресс-бары
- 🔧 **Configurable** - YAML конфиги, шаблоны сообщений

## 🚀 Быстрый старт

```
# Установка
pip install websocket-client pyyaml

# Клонирование
git clone https://github.com/lainmodegod/lainmodewebsocketridder.git
cd lainmodewebsocketridder

# Запуск с конфигом
python3 lainmodewebsocketridder.py -c config.yaml

# Или с параметрами
python3 lainmodewebsocketridder.py \
  -u wss://api.target.com/ws \
  -t "your_token" \
  --chats chats.txt \
  --users users.txt
```
   📖 Пример использования
```
from lainmodewebsocketridder import LainModeWebSocketRiddler, TestConfig, TargetConfig

# Создаем конфиг
config = TestConfig(
    url="wss://api.target.com/websocket",
    token="your_token",
    targets=TargetConfig(
        chats=[12345, 67890],
        users=[54321, 98765]
    ),
    test_messages=[
        {
            "opcode": 79,
            "payload": {"chatIds": ["{target}"]},
            "name": "chat_history",
            "type": "chat"
        }
    ]
)

# Запускаем
riddler = LainModeWebSocketRiddler(config)
results = riddler.run()
riddler.print_summary()
```
🎯 Примеры конфигов
Для Telegram/MAX подобных API:
```
url: "wss://ws-api.example.com/websocket"
test_messages:
  - opcode: 79
    payload: {"chatIds": ["{target}"]}
    name: "chat_history"
    type: "chat"
  - opcode: 48
    payload: {"userId": "{target}"}
    name: "user_profile"
    type: "user"
```
Для Discord подобных:
```
    test_messages:
  - opcode: 8
    payload: {"channel_id": "{target}"}
    name: "channel_messages"
    type: "channel"
  - opcode: 14
    payload: {"guild_id": "{target}"}
    name: "guild_info"
    type: "guild"
```
    📊 Результаты

После выполнения в папке results/ появятся:

  results_TIMESTAMP.json - все данные в JSON

  report_TIMESTAMP.md - красивый Markdown отчет

  summary_TIMESTAMP.txt - краткое резюме

  🤝 Как помочь проекту

  ⭐ Поставь звезду

  🐛 Сообщай о багах

  💡 Предлагай идеи

  🔧 Отправляй PR

  📜 Лицензия

MIT © 2026 lainmode


requirements

websocket-client>=1.6.0
pyyaml>=6.0
colorama>=0.4.6
tqdm>=4.65.0
