# Kaspersky Full Scan Responder for TheHive

## Описание проекта

Этот скрипт kaspersky_scan_responder.py — Responder для TheHive, который позволяет запускать полное антивирусное сканирование Kaspersky Endpoint Security (KES) на Linux-хосте по команде из TheHive.  
Скрипт автоматизирует запуск задачи проверки, отслеживание её статуса, получение итоговой статистики и запись логов.

---

## Что делает скрипт

- Запускает задачу полной проверки Kaspersky Endpoint Security через консольную утилиту kesl-control.
- Периодически проверяет статус задачи, ожидает её завершения.
- Получает и парсит статистику проверки: количество обработанных объектов, обнаруженных угроз, вылеченных, удаленных и пр.
- Записывает подробный лог в файл /tmp/kaspersky_scan_log_<timestamp>.log.
- Возвращает результаты в виде структурированного JSON с ключевыми метриками и сообщением.
- Предназначен для интеграции в SOC-системы, такие как TheHive и Cortex.

---

## Требования

- Linux с установленным Kaspersky Endpoint Security и доступом к kesl-control.
- Права на выполнение команд sudo kesl-control --start-task и прочих (лучше без запроса пароля для удобства автоматизации).
- Python 3.x.

---

## Установка

1. Скопируйте файл kaspersky_scan_responder.py на целевой Linux-хост с Kaspersky.
2. Убедитесь, что у пользователя есть права на запуск sudo kesl-control.
3. Проверьте, что Python 3 установлен (python3 --version).

---

## Пример запуска

```
bash
python3 kaspersky_scan_responder.py
```

## Результат

```
json
{
  "success": true,
  "message": "Проверка завершена.\nОбъектов обработано: 1234\nОбнаружено угроз: 5\nЗаражено: 3\nВылечено: 2, Удалено: 1, Не вылечено: 0\nОшибок: 0",
  "statistics": {
    "processed_objects": 1234,
    "detected_threats": 5,
    "infected_objects": 3,
    "cured_objects": 2,
    "deleted_objects": 1,
    "not_cured": 0,
    "scan_errors": 0
  },
  "scan_log": "...полный лог сканирования...",
  "log_file_path": "/tmp/kaspersky_scan_log_20250526_123456.log"
}
```
