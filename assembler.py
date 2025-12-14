"""
Ассемблер для Учебной Виртуальной Машины (УВМ) - Этап 2
"""

import argparse
import sys
import os
from typing import List, Dict, Any, Tuple
from parser import Parser
from constants import *

class Assembler:
    """Улучшенный ассемблер УВМ с формированием машинного кода"""
    
    def __init__(self):
        self.command_count = 0
    
    @staticmethod
    def _to_twos_complement(value: int, bits: int) -> int:
        """Преобразование в дополнительный код"""
        if value >= 0:
            return value & ((1 << bits) - 1)
        else:
            return ((1 << bits) + value) & ((1 << bits) - 1)
    
    @staticmethod
    def _from_twos_complement(value: int, bits: int) -> int:
        """Преобразование из дополнительного кода"""
        if value & (1 << (bits - 1)):
            return value - (1 << bits)
        return value
    
    def assemble_load_const(self, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды загрузки константы"""
        addr = int(fields['addr'])
        const = int(fields['const'])
        
        # Проверка диапазонов
        if not (0 <= addr <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Адрес {addr} вне диапазона (0-{(1 << FIELD_SIZES['B']) - 1})")
        
        const_tc = self._to_twos_complement(const, FIELD_SIZES['C'])
        
        self.command_count += 1
        return {
            'A': OP_LOAD_CONST,
            'B': addr,
            'C': const_tc,
            'D': 0  # Не используется
        }
    
    def assemble_read_mem(self, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды чтения из памяти"""
        dest = int(fields['dest'])
        addr = int(fields['addr'])
        offset = int(fields['offset'])
        
        # Проверка диапазонов
        if not (0 <= offset <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Смещение {offset} вне диапазона (0-{(1 << FIELD_SIZES['B']) - 1})")
        if not (0 <= addr <= (1 << FIELD_SIZES['C']) - 1):
            raise ValueError(f"Адрес {addr} вне диапазона (0-{(1 << FIELD_SIZES['C']) - 1})")
        if not (0 <= dest <= (1 << FIELD_SIZES['D']) - 1):
            raise ValueError(f"Адрес назначения {dest} вне диапазона (0-{(1 << FIELD_SIZES['D']) - 1})")
        
        self.command_count += 1
        return {
            'A': OP_READ_MEM,
            'B': offset,
            'C': addr,
            'D': dest
        }
    
    def assemble_write_mem(self, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды записи в память"""
        addr = int(fields['addr'])
        offset = int(fields['offset'])
        src = int(fields['src'])
        
        # Проверка диапазонов
        if not (0 <= src <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Адрес источника {src} вне диапазона (0-{(1 << FIELD_SIZES['B']) - 1})")
        if not (0 <= addr <= (1 << FIELD_SIZES['C']) - 1):
            raise ValueError(f"Адрес {addr} вне диапазона (0-{(1 << FIELD_SIZES['C']) - 1})")
        if not (0 <= offset <= (1 << FIELD_SIZES['D']) - 1):
            raise ValueError(f"Смещение {offset} вне диапазона (0-{(1 << FIELD_SIZES['D']) - 1})")
        
        self.command_count += 1
        return {
            'A': OP_WRITE_MEM,
            'B': src,
            'C': addr,
            'D': offset
        }
    
    def assemble_bitreverse(self, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды обращения битов"""
        dest = int(fields['dest'])
        src = int(fields['src'])
        
        # Проверка диапазонов
        if not (0 <= src <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Адрес источника {src} вне диапазона (0-{(1 << FIELD_SIZES['B']) - 1})")
        if not (0 <= dest <= (1 << FIELD_SIZES['C']) - 1):
            raise ValueError(f"Адрес назначения {dest} вне диапазона (0-{(1 << FIELD_SIZES['C']) - 1})")
        
        self.command_count += 1
        return {
            'A': OP_BITREVERSE,
            'B': src,
            'C': dest,
            'D': 0  # Не используется
        }
    
    def assemble_command(self, parsed_cmd: Dict[str, Any]) -> Dict[str, int]:
        """Ассемблирование одной команды"""
        assemblers = {
            'load_const': self.assemble_load_const,
            'read_mem': self.assemble_read_mem,
            'write_mem': self.assemble_write_mem,
            'bitreverse': self.assemble_bitreverse
        }
        
        op_type = parsed_cmd['op_type']
        if op_type not in assemblers:
            raise ValueError(f"Неизвестный тип операции: {op_type}")
        
        return assemblers[op_type](parsed_cmd)
    
    def pack_command(self, fields: Dict[str, int]) -> bytes:
        """Упаковка полей команды в 7 байт (машинный код)"""
        # Объединяем поля в одно 56-битное значение
        value = 0
        if fields['A'] == OP_READ_MEM:
                for field, offset in FIELD_OFFSETS1.items():
                    if field in fields:
                        field_value = fields[field] & ((1 << FIELD_SIZES[field]) - 1)
                        value |= field_value << offset
        else:
            for field, offset in FIELD_OFFSETS.items():
                if field in fields:
                    field_value = fields[field] & ((1 << FIELD_SIZES[field]) - 1)
                    value |= field_value << offset
        
        # Преобразуем в 7 байт (little-endian)
        result = bytearray(7)
        for i in range(7):
            result[i] = (value >> (8 * i)) & 0xFF
        
        return bytes(result)
    
    def assemble_to_machine_code(self, parsed_commands: List[Dict[str, Any]]) -> Tuple[bytes, List[bytes]]:
        """
        Ассемблирование всей программы в машинный код
        
        Возвращает:
        - bytes: бинарные данные программы
        - List[bytes]: список команд в байтовом формате
        """
        binary_commands = []
        binary_data = bytearray()
        
        self.command_count = 0
        
        for parsed_cmd in parsed_commands:
            fields = self.assemble_command(parsed_cmd)
            packed_command = self.pack_command(fields)
            binary_commands.append(packed_command)
            binary_data.extend(packed_command)
        
        return bytes(binary_data), binary_commands
    
    def display_machine_code(self, binary_commands: List[bytes], show_human_readable: bool = False):
        """Отображение машинного кода в удобном формате"""
        print(f"\n=== Машинный код ({len(binary_commands)} команд) ===")
        
        for i, cmd_bytes in enumerate(binary_commands):
            print(f"\nКоманда {i}:")
            
            # Байтовое представление
            hex_bytes = ', '.join(f'0x{b:02X}' for b in cmd_bytes)
            print(f"  Байты: {hex_bytes}")
            
            if show_human_readable:
                # Человекочитаемое представление полей
                fields = self.extract_fields(cmd_bytes)
                print(f"  Поля: A={fields['A']}, B={fields['B']}, ", end="")
                
                # Для загрузки константы показываем реальное значение
                if fields['A'] == OP_LOAD_CONST:
                    const_value = self._from_twos_complement(fields['C'], FIELD_SIZES['C'])
                    print(f"C={const_value} ({fields['C']:#x})")
                else:
                    print(f"C={fields['C']}, D={fields['D']}")
    
    def extract_fields(self, command_bytes: bytes) -> Dict[str, int]:
        """Извлечение полей из байтов команды (обратная операция)"""
        if len(command_bytes) != 7:
            raise ValueError("Команда должна быть длиной 7 байт")
        
        # Объединяем байты в одно значение
        value = 0
        for i, byte in enumerate(command_bytes):
            value |= byte << (8 * i)
        
        # Извлекаем поля
        fields = {}
        for field, offset in FIELD_OFFSETS.items():
            mask = (1 << FIELD_SIZES[field]) - 1
            fields[field] = (value >> offset) & mask
        
        return fields


def main():
    """Точка входа CLI-приложения для этапа 2"""
    parser = argparse.ArgumentParser(
        description='Ассемблер Учебной Виртуальной Машины - Этап 2: Формирование машинного кода'
    )
    parser.add_argument('input_file', help='Путь к исходному файлу с текстом программы')
    parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования (вывод машинного кода в байтовом формате)')
    
    args = parser.parse_args()

    try:
        # Чтение исходного файла
        if not os.path.exists(args.input_file):
            raise FileNotFoundError(f"Файл не найден: {args.input_file}")
        
        with open(args.input_file, 'r', encoding='utf-8') as f:
            program_text = f.read()
        
        # Разбор программы
        parsed_commands = Parser.parse_program(program_text)
        
        if not parsed_commands:
            print("Предупреждение: программа не содержит команд")
        
        # Ассемблирование в машинный код
        assembler = Assembler()
        binary_data, binary_commands = assembler.assemble_to_machine_code(parsed_commands)
        
        # Запись результата
        with open(args.output_file, 'wb') as f:
            f.write(binary_data)
        
        # Вывод информации
        print(f"Ассемблирование завершено успешно!")
        print(f"Количество команд: {assembler.command_count}")
        print(f"Размер выходного файла: {len(binary_data)} байт")
        
        # Вывод в режиме тестирования
        if args.test:
            assembler.display_machine_code(binary_commands, show_human_readable=True)
            
            # Дополнительно выводим бинарный дамп
            print(f"\n=== Бинарный дамп файла {args.output_file} ===")
            print(f"Смещение  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
            print("-" * 60)
            
            for i in range(0, len(binary_data), 16):
                # Смещение
                print(f"{i:08X}: ", end="")
                
                # Байты в hex
                for j in range(16):
                    if i + j < len(binary_data):
                        print(f"{binary_data[i + j]:02X} ", end="")
                    else:
                        print("   ", end="")
                
                # ASCII представление
                print(" ", end="")
                for j in range(16):
                    if i + j < len(binary_data):
                        b = binary_data[i + j]
                        if 32 <= b <= 126:
                            print(chr(b), end="")
                        else:
                            print(".", end="")
                    else:
                        print(" ", end="")
                
                print()
        
        print(f"\nРезультат записан в файл: {args.output_file}")
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()