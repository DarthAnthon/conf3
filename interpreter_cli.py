"""
Интерпретатор УВМ с поддержкой командной строки
"""

import argparse
import sys
import json
from typing import List, Tuple, Dict
from assembler import Assembler
from constants import *

class UVMInterpreterCLI:
    """Интерпретатор УВМ с полным циклом выполнения и дампом памяти"""
    
    def __init__(self, memory_size: int = 65536):
        self.memory = [0] * memory_size
        self.pc = 0  # Программный счетчик
        self.assembler = Assembler()
    
    def extract_fields(self, command_bytes: bytes) -> dict:
        """Извлечение полей из 7 байт команды"""
        if len(command_bytes) != 7:
            raise ValueError(f"Команда должна быть длиной 7 байт, получено {len(command_bytes)}")
        
        # Объединяем байты в одно значение
        value = 0
        for i, byte in enumerate(command_bytes):
            value |= byte << (8 * i)
        # Извлекаем поля
        fields = {}
        # Определяем, какую таблицу смещений использовать
        opcode = value & ((1 << FIELD_SIZES['A']) - 1)
        
        # Для команды чтения памяти используем особый формат
        if opcode == OP_READ_MEM:
            for field, offset in FIELD_OFFSETS1.items():
                mask = (1 << FIELD_SIZES1[field]) - 1
                fields[field] = (value >> offset) & mask
        else:
            for field, offset in FIELD_OFFSETS.items():
                mask = (1 << FIELD_SIZES[field]) - 1
                fields[field] = (value >> offset) & mask
        return fields
    
    def bitreverse_16(self, value: int) -> int:
        """Обращение битов 16-битного числа"""
        result = 0
        for i in range(16):
            if value & (1 << i):
                result |= 1 << (15 - i)
        return result & BITREVERSE_MASK
    
    def execute_command(self, ind) -> bool:
        """Выполнение одной команды"""
        opcode = self.memory[300+ind*4]
        
        try:
            if opcode == OP_LOAD_CONST:
                # Загрузка константы: [addr] = const
                addr = self.memory[301+ind*4]
                const = self.memory[302+ind*4]
                # Преобразование из дополнительного кода
                const = self.assembler._from_twos_complement(const, FIELD_SIZES['C'])
                self.memory[addr] = const
                
            elif opcode == OP_READ_MEM:
                # Чтение из памяти: [dest] = [[addr] + offset]
                offset = self.memory[301+ind*4]
                addr_ptr = self.memory[302+ind*4]
                dest = self.memory[303+ind*4]
                
                # Вычисляем адрес: значение по адресу addr_ptr + offset
                base_addr = self.memory[addr_ptr]
                src_addr = base_addr + offset
                self.memory[dest] = self.memory[src_addr]
                
            elif opcode == OP_WRITE_MEM:
                # Запись в память: [[addr] + offset] = [src]
                src = self.memory[301+ind*4]
                addr_ptr = self.memory[302+ind*4]
                offset = self.memory[303+ind*4]
                
                # Вычисляем адрес назначения: значение по адресу addr_ptr + offset
                base_addr = self.memory[addr_ptr]
                dest_addr = base_addr + offset
                self.memory[dest_addr] = self.memory[src]
                
            elif opcode == OP_BITREVERSE:
                # Обращение битов: [dest_ptr] = bitreverse([src])
                src = self.memory[301+ind*4]
                dest_ptr = self.memory[302+ind*4]
                
                # Получаем значение, обращаем биты, записываем
                value = self.memory[src]
                reversed_value = self.bitreverse_16(value)
                #self.memory[dest_ptr] = reversed_value
                self.memory[dest_ptr] = reversed_value

            else:
                print(f"Неизвестный код операции: {opcode}")
                return False
            
            return True
            
        except IndexError as e:
            print(f"Ошибка доступа к памяти: {e}")
            return False
        except Exception as e:
            print(f"Ошибка выполнения команды: {e}")
            return False
    
    def run(self, binary_file: str):
        """Запуск интерпретатора"""
        self.pc = 0
        command_count = 0
        
        with open(binary_file, 'rb') as f:
            binary_data = f.read()

        # Проверяем, что размер кратен 7 байтам (размер команды)
        if len(binary_data) % 7 != 0:
            print(f"Предупреждение: размер файла {len(binary_data)} байт не кратен 7")

        for i in range(0, len(binary_data), 7):
            command_bytes = binary_data[i:i+7]
            fields = self.extract_fields(command_bytes)
            
            self.memory[300+i*4//7] = fields['A']
            self.memory[301+i*4//7] = fields['B']
            self.memory[302+i*4//7] = fields['C']
            self.memory[303+i*4//7] = fields['D']

            # Выполняем команду
            success = self.execute_command(i//7)
            if not success:
                print(f"Остановка выполнения на команде {self.pc}")
                break
            
            self.pc += 1
            command_count += 1
        
        print(f"Выполнено {command_count} команд")
    
    def dump_memory(self, start_addr: int, end_addr: int) -> Dict[str, int]:
        """Создание дампа памяти в указанном диапазоне"""
        if start_addr < 0 or end_addr >= len(self.memory) or start_addr > end_addr:
            raise ValueError(f"Некорректный диапазон адресов: {start_addr}-{end_addr}")
        
        dump = {}
        for addr in range(start_addr, end_addr + 1):
            dump[str(addr)] = self.memory[addr]
        
        return dump
    
    def save_memory_dump(self, output_file: str, start_addr: int, end_addr: int):
        """Сохранение дампа памяти в JSON файл"""
        dump_data = self.dump_memory(start_addr, end_addr)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dump_data, f, indent=2, ensure_ascii=False)
        
        print(f"Дамп памяти сохранен в {output_file} (адреса {start_addr}-{end_addr})")
    
    def run_program(self, binary_file: str, output_file: str, 
                    start_addr: int = 0, end_addr: int = 100):
        """Полный цикл выполнения программы"""
        # Загрузка программы и выполнение программы
        self.run(binary_file)
        
        # Сохранение дампа памяти
        self.save_memory_dump(output_file, start_addr, end_addr)





def main():
    """Точка входа CLI-интерпретатора"""
    parser = argparse.ArgumentParser(
        description='Интерпретатор Учебной Виртуальной Машины (УВМ)'
    )
    parser.add_argument('binary_file', nargs='?', help='Путь к бинарному файлу с программой')
    parser.add_argument('output_file', nargs='?', help='Путь к JSON файлу для дампа памяти')
    parser.add_argument('--start', type=int, default=0, 
                       help='Начальный адрес для дампа памяти (по умолчанию: 0)')
    parser.add_argument('--end', type=int, default=100,
                       help='Конечный адрес для дампа памяти (по умолчанию: 100)')
    
    args = parser.parse_args()

    try:
        # Создаем и запускаем интерпретатор
        interpreter = UVMInterpreterCLI()
        
        # Выполняем программу
        interpreter.run_program(
            binary_file=args.binary_file,
            output_file=args.output_file,
            start_addr=args.start,
            end_addr=args.end
        )
        
        # Выводим информацию о выполнении
        print(f"\nИнформация о выполнении:")
        print(f"- Выполнено команд: {interpreter.pc}")
        print(f"- Диапазон дампа: {args.start}-{args.end}")
        
    except FileNotFoundError as e:
        print(f"Ошибка: файл не найден - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()