"""
Ассемблер для Учебной Виртуальной Машины (УВМ)
"""

import argparse
import sys
from typing import List, Dict, Any
from parser import Parser
from constants import *

class Assembler:
    """Ассемблер УВМ"""
    
    @staticmethod
    def _to_twos_complement(value: int, bits: int) -> int:
        """Преобразование в дополнительный код"""
        if value >= 0:
            return value & ((1 << bits) - 1)
        else:
            return ((1 << bits) + value) & ((1 << bits) - 1)
    
    @classmethod
    def assemble_load_const(cls, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды загрузки константы"""
        addr = int(fields['addr'])
        const = int(fields['const'])
        
        # Проверка диапазонов
        if not (0 <= addr <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Адрес {addr} вне диапазона")
        
        const_tc = cls._to_twos_complement(const, FIELD_SIZES['C'])
        
        return {
            'A': OP_LOAD_CONST,
            'B': addr,
            'C': const_tc,
            'D': 0  # Не используется
        }
    
    @classmethod
    def assemble_read_mem(cls, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды чтения из памяти"""
        dest = int(fields['dest'])
        addr = int(fields['addr'])
        offset = int(fields['offset'])
        
        # Проверка диапазонов
        if not (0 <= offset <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Смещение {offset} вне диапазона")
        if not (0 <= addr <= (1 << FIELD_SIZES['C']) - 1):
            raise ValueError(f"Адрес {addr} вне диапазона")
        if not (0 <= dest <= (1 << FIELD_SIZES['D']) - 1):
            raise ValueError(f"Адрес назначения {dest} вне диапазона")
        
        return {
            'A': OP_READ_MEM,
            'B': offset,
            'C': addr,
            'D': dest
        }
    
    @classmethod
    def assemble_write_mem(cls, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды записи в память"""
        addr = int(fields['addr'])
        offset = int(fields['offset'])
        src = int(fields['src'])
        
        # Проверка диапазонов
        if not (0 <= src <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Адрес источника {src} вне диапазона")
        if not (0 <= addr <= (1 << FIELD_SIZES['C']) - 1):
            raise ValueError(f"Адрес {addr} вне диапазона")
        if not (0 <= offset <= (1 << FIELD_SIZES['D']) - 1):
            raise ValueError(f"Смещение {offset} вне диапазона")
        
        return {
            'A': OP_WRITE_MEM,
            'B': src,
            'C': addr,
            'D': offset
        }
    
    @classmethod
    def assemble_bitreverse(cls, fields: Dict[str, str]) -> Dict[str, int]:
        """Ассемблирование команды обращения битов"""
        dest = int(fields['dest'])
        src = int(fields['src'])
        
        # Проверка диапазонов
        if not (0 <= src <= (1 << FIELD_SIZES['B']) - 1):
            raise ValueError(f"Адрес источника {src} вне диапазона")
        if not (0 <= dest <= (1 << FIELD_SIZES['C']) - 1):
            raise ValueError(f"Адрес назначения {dest} вне диапазона")
        
        return {
            'A': OP_BITREVERSE,
            'B': src,
            'C': dest,
            'D': 0  # Не используется
        }
    
    @classmethod
    def assemble_command(cls, parsed_cmd: Dict[str, Any]) -> Dict[str, int]:
        """Ассемблирование одной команды"""
        assemblers = {
            'load_const': cls.assemble_load_const,
            'read_mem': cls.assemble_read_mem,
            'write_mem': cls.assemble_write_mem,
            'bitreverse': cls.assemble_bitreverse
        }
        
        op_type = parsed_cmd['op_type']
        if op_type not in assemblers:
            raise ValueError(f"Неизвестный тип операции: {op_type}")
        
        return assemblers[op_type](parsed_cmd)
    
    @classmethod
    def pack_command(cls, fields: Dict[str, int]) -> bytes:
        """Упаковка полей команды в 7 байт"""
        # Объединяем поля в одно 56-битное значение
        value = 0
        for field, offset in FIELD_OFFSETS.items():
            if field in fields:
                field_value = fields[field] & ((1 << FIELD_SIZES[field]) - 1)
                value |= field_value << offset
        
        # Преобразуем в 7 байт (little-endian)
        result = bytearray(7)
        for i in range(7):
            result[i] = (value >> (8 * i)) & 0xFF
        
        return bytes(result)
    
    @classmethod
    def assemble_program(cls, parsed_commands: List[Dict[str, Any]]) -> bytes:
        """Ассемблирование всей программы"""
        binary_data = bytearray()
        
        for parsed_cmd in parsed_commands:
            fields = cls.assemble_command(parsed_cmd)
            binary_data.extend(cls.pack_command(fields))
        
        return bytes(binary_data)


def main():
    """Точка входа CLI-приложения"""
    parser = argparse.ArgumentParser(description='Ассемблер Учебной Виртуальной Машины')
    parser.add_argument('input_file', help='Путь к исходному файлу с текстом программы')
    parser.add_argument('output_file', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования (вывод внутреннего представления)')
    
    args = parser.parse_args()
    
    try:
        # Чтение исходного файла
        with open(args.input_file, 'r', encoding='utf-8') as f:
            program_text = f.read()
        
        # Разбор программы
        parsed_commands = Parser.parse_program(program_text)
        
        # Ассемблирование
        assembler = Assembler()
        binary_data = assembler.assemble_program(parsed_commands)
        
        # Запись результата
        with open(args.output_file, 'wb') as f:
            f.write(binary_data)
        
        # Вывод в режиме тестирования
        if args.test:
            print("=== Внутреннее представление программы ===")
            for i, parsed_cmd in enumerate(parsed_commands):
                print(f"\nКоманда {i}:")
                print(f"  Тип: {parsed_cmd['op_type']}")
                for key, value in parsed_cmd.items():
                    if key != 'op_type':
                        print(f"  {key}: {value}")
                
                # Показываем бинарное представление
                fields = assembler.assemble_command(parsed_cmd)
                packed = assembler.pack_command(fields)
                print(f"  Байты: {', '.join(f'0x{b:02X}' for b in packed)}")
        
        print(f"\nПрограмма успешно ассемблирована в {args.output_file}")
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()