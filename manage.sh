#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

set -e

show_usage() {
    echo -e "${YELLOW}Использование: $0 {setup|run|down|logs}${NC}"
    echo "  setup - Первоначальная настройка проекта (venv, зависимости, Docker)."
    echo "  run   - Запуск приложения (Flask + WebSocket + Worker)."
    echo "  down  - Остановка и удаление Docker-контейнера MongoDB."
    echo "  logs  - Просмотр логов MongoDB в реальном времени."
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

case "$1" in
    setup)
        echo -e "${GREEN}--- Настройка проекта... ---${NC}"

        if ! command_exists python3; then
            echo -e "${RED}Ошибка: python3 не найден. Пожалуйста, установите Python 3.${NC}"
            exit 1
        fi

        if ! command_exists docker-compose; then
            echo -e "${RED}Ошибка: docker-compose не найден. Пожалуйста, установите Docker и Docker Compose.${NC}"
            exit 1
        fi

        echo "1. Создание виртуального окружения 'venv'..."
        python3 -m venv venv

        echo "2. Установка зависимостей из requirements.txt..."
        # Запускаем установку в subshell, чтобы активация venv не повлияла
        # на текущую сессию терминала.
        (
            source venv/bin/activate
            pip install -r requirements.txt
        )

        echo "3. Запуск MongoDB через docker-compose..."
        docker-compose up -d

        echo -e "${GREEN}--- Настройка успешно завершена! ---${NC}"
        echo -e "Теперь вы можете запустить проект командой: ${YELLOW}./manage.sh run${NC}"
        ;;

    run)
        echo -e "${GREEN}--- Запуск приложения... ---${NC}"
        if [ ! -d "venv" ]; then
            echo -e "${RED}Ошибка: Виртуальное окружение 'venv' не найдено.${NC}"
            echo -e "Пожалуйста, сначала выполните: ${YELLOW}./manage.sh setup${NC}"
            exit 1
        fi

        # Активируем venv и запускаем приложение.
        source venv/bin/activate
        exec python3 run.py
        ;;

    down)
        echo -e "${YELLOW}--- Остановка сервисов Docker... ---${NC}"
        docker-compose down
        echo -e "${GREEN}--- Сервисы успешно остановлены. ---${NC}"
        ;;

    logs)
        echo -e "${YELLOW}--- Просмотр логов MongoDB (нажмите Ctrl+C для выхода)... ---${NC}"
        docker-compose logs -f mongo
        ;;

    *)
        # Если передан неизвестный аргумент или аргументов нет
        show_usage
        exit 1
        ;;
esac