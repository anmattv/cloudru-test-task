#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import os
import sys
import re
from datetime import datetime


class KasperskyResponder:
    def __init__(self):
        self.task_name = "Full Scan"  
        self.check_interval = 5
        self.max_checks = 240

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = f"/tmp/kaspersky_scan_log_{timestamp}.log"

    def run_cmd(self, cmd):
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            return True, output
        except subprocess.CalledProcessError as e:
            return False, e.output

    def start_scan(self):
        cmd = f"sudo kesl-control --start-task \"{self.task_name}\""
        return self.run_cmd(cmd)

    def get_task_info(self):
        cmd = f"sudo kesl-control --get-task-info \"{self.task_name}\""
        return self.run_cmd(cmd)

    def get_statistics(self):
        cmd = f"sudo kesl-control --get-task-statistics \"{self.task_name}\""
        return self.run_cmd(cmd)

    def wait_for_completion(self):
        log = []
        for attempt in range(self.max_checks):
            success, output = self.get_task_info()
            if not success:
                log.append("Ошибка получения статуса задачи")
                return False, "\n".join(log)

            log.append(output.strip())

            if "Completed" in output or "Завершена" in output:
                return True, "\n".join(log)

            time.sleep(self.check_interval)

        log.append("Таймаут ожидания завершения задачи")
        return False, "\n".join(log)

    def parse_statistics(self, output):
        result = {}

        patterns = {
            'processed_objects': r'Обработано объектов\s*:\s*(\d+)',
            'detected_threats': r'Обнаружено угроз\s*:\s*(\d+)',
            'infected_objects': r'Заражено объектов\s*:\s*(\d+)',
            'cured_objects': r'Объектов вылечено\s*:\s*(\d+)',
            'deleted_objects': r'Удалено объектов\s*:\s*(\d+)',
            'not_cured': r'Не удалось вылечить объектов\s*:\s*(\d+)',
            'scan_errors': r'Ошибок проверки\s*:\s*(\d+)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            result[key] = int(match.group(1)) if match else 0

        return result

    def run(self, request=None):
        full_log = []

        success, msg = self.start_scan()
        if not success:
            return self._error("Не удалось запустить задачу", msg)

        full_log.append(msg)

        success, status_log = self.wait_for_completion()
        full_log.append(status_log)

        if not success:
            return self._error("Проверка не завершена", "\n".join(full_log))

        success, stats_output = self.get_statistics()
        if not success:
            return self._error("Не удалось получить статистику", stats_output)

        full_log.append(stats_output)
        with open(self.log_file, "w") as f:
            f.write("\n".join(full_log))

        stats = self.parse_statistics(stats_output)

        summary = (
            f"Проверка завершена.\n"
            f"Объектов обработано: {stats['processed_objects']}\n"
            f"Обнаружено угроз: {stats['detected_threats']}\n"
            f"Заражено: {stats['infected_objects']}\n"
            f"Вылечено: {stats['cured_objects']}, Удалено: {stats['deleted_objects']}, Не вылечено: {stats['not_cured']}\n"
            f"Ошибок: {stats['scan_errors']}"
        )

        return {
            "success": True,
            "message": summary,
            "statistics": stats,
            "scan_log": "\n".join(full_log),
            "log_file_path": self.log_file
        }

    def _error(self, message, details=""):
        return {
            "success": False,
            "message": message,
            "details": details
        }


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
    except Exception:
        request = {}

    responder = KasperskyResponder()
    result = responder.run(request)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
