# Конфигурационное управление работа №3 

# Этап 2 Формирование машинного кода
Реализация ассемблера и интерпретатора для учебной виртуальной машины. Преобразование промежуточное представления в бинарный машинный код УВМ.

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
python "c:/Users/Anton/Desktop/учёба/конф/пр 3/assembler.py" complex_program.asm program.bin --test

### Пример работы
<img width="464" height="793" alt="image" src="https://github.com/user-attachments/assets/4c98d752-abd7-40aa-84eb-f96f5c009aec" />


<img width="482" height="693" alt="image" src="https://github.com/user-attachments/assets/110592cf-00b1-46cb-8080-56acfd0bcf0b" />


<img width="691" height="268" alt="image" src="https://github.com/user-attachments/assets/468effdf-5314-4c1d-ab93-0731024432ca" />


