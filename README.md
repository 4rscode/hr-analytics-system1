## Установка

1. Установите зависимости:

   ```bash
   python -m pip install -r requirements.txt
   ```

## Запуск

Для запуска приложения выполните следующую команду:

```bash
python start.py
```

#Это MVP проекта он требудет доработки

# Resume Analytics MVP

## Описание

**Resume Analytics MVP** — это минимально жизнеспособный продукт (MVP) для автоматизированного анализа резюме. Проект направлен на извлечение ключевой информации из резюме, оценку кандидатов по заданным критериям и предоставление рекомендаций по курсам для улучшения их квалификации. На текущий момент система является прототипом и требует доработки.

## Как это работает

Система функционирует следующим образом:

1. **Анализ резюме**: С использованием API OpenAI резюме анализируется, и из него выделяется основная информация (например, образование, навыки, опыт работы).
2. **Оценка кандидатов**: На основе матриц по различным разделам (таким как образование и навыки) каждому кандидату присваивается оценка.
3. **Рекомендации**: В зависимости от полученных оценок система рекомендует курсы для прохождения, чтобы улучшить компетенции кандидата.

## Текущий статус

Проект находится на стадии MVP и нуждается в дальнейшем развитии, включая:
- Калибровку системы для повышения точности анализа и рекомендаций.
- Возможные улучшения, такие как расширение матриц оценок или интеграция локальной модели (например, LLaMA).

## Технологии

- **Python**: основной язык разработки.
- **API OpenAI**: используется для анализа текста резюме.

## Возможности для улучшения

Система может быть доработана в следующих направлениях:
- **Калибровка**: Улучшение алгоритмов для более точных оценок.
- **Расширение матриц**: Добавление новых критериев для более детального анализа.
- **Интеграция локальной модели**: Использование моделей, таких как LLaMA, для повышения производительности и независимости от внешних API.

## Лицензия

Проект распространяется под лицензией [MIT](LICENSE).
