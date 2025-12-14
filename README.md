# Конфигурационное управление работа №3 

# Этап 5 Выполнение тестовой задачи
Реализация ассемблера и интерпретатора для учебной виртуальной машины. Преобразование промежуточное представления в бинарный машинный код УВМ. Цикл интерпретации, модель памяти УВМ и базовые команды. Поддержка 
вычислительных операций. Решение тестовой задачи.

## Язык ассемблера УВМ

### 1. Загрузка константы

Пример: `[201] = 567`

### 2. Чтение из памяти

Пример: `[386] = [[962] + 21]`

### 3. Запись в память

Пример: `[[226] + 54] = [217]`

### 4. Обращение битов

Пример: `[735] = bitreverse([980])`

## Использование

### Запуск тестов:
#### Тест 1
python assembler.py test_1.asm program_1.bin 

python interpreter_cli.py program_1.bin dump_1.json --start 0 --end 450

#### Тест 2
python assembler.py test_2.asm program_2.bin 

python interpreter_cli.py program_2.bin dump_2.json --start 0 --end 450

#### Тест 3
python assembler.py test_3.asm program_3.bin 

python interpreter_cli.py program_3.bin dump_3.json --start 0 --end 450

### Пример работы
<img width="1101" height="859" alt="image" src="https://github.com/user-attachments/assets/ee25f70d-ac4f-4487-899a-5a1217b9a829" />





