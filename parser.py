"""
Парсер языка ассемблера УВМ с поддержкой шестнадцатеричных чисел
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from constants import *

class Parser:
    """Улучшенный парсер ассемблерных команд с поддержкой разных форматов чисел"""
    
    # Паттерны для разбора команд с поддержкой hex
    PATTERNS = {
        'load_const': re.compile(
            r'^\[\s*(?P<addr>\d+|0x[0-9a-fA-F]+)\s*\]\s*=\s*(?P<const>-?\d+|0x[0-9a-fA-F]+)\s*$'
        ),
        'read_mem': re.compile(
            r'^\[\s*(?P<dest>\d+|0x[0-9a-fA-F]+)\s*\]\s*=\s*\[\s*\[\s*(?P<addr>\d+|0x[0-9a-fA-F]+)\s*\]\s*\+\s*(?P<offset>\d+|0x[0-9a-fA-F]+)\s*\]\s*$'
        ),
        'write_mem': re.compile(
            r'^\[\s*\[\s*(?P<addr>\d+|0x[0-9a-fA-F]+)\s*\]\s*\+\s*(?P<offset>\d+|0x[0-9a-fA-F]+)\s*\]\s*=\s*\[\s*(?P<src>\d+|0x[0-9a-fA-F]+)\s*\]\s*$'
        ),
        'bitreverse': re.compile(
            r'^\[\s*(?P<dest>\d+|0x[0-9a-fA-F]+)\s*\]\s*=\s*bitreverse\(\s*\[\s*(?P<src>\d+|0x[0-9a-fA-F]+)\s*\]\s*\)\s*$'
        )
    }
    
    @staticmethod
    def parse_number(value: str) -> int:
        """
        Парсит число из строки, поддерживая разные форматы:
        - Десятичные: 123, -456
        - Шестнадцатеричные: 0x123, 0xFF, 0x1a
        """
        value = value.strip()
        
        if value.startswith('0x') or value.startswith('0X'):
            # Шестнадцатеричное число
            return int(value, 16)
        else:
            # Десятичное число (может быть отрицательным)
            return int(value)
    
    @classmethod
    def parse_line(cls, line: str) -> Optional[Dict[str, Any]]:
        """
        Разбор строки ассемблерного кода
        
        Возвращает словарь с полями команды или None, если строка не является командой
        """
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith(';') or line.startswith('//'):
            return None
        
        # Удаляем комментарии в конце строки
        for comment_marker in [';', '//']:
            if comment_marker in line:
                line = line.split(comment_marker)[0].strip()
        
        # Пробуем каждый паттерн
        for op_type, pattern in cls.PATTERNS.items():
            match = pattern.match(line)
            if match:
                result = {'op_type': op_type}
                # Парсим все числовые поля
                for key, value in match.groupdict().items():
                    result[key] = cls.parse_number(value)
                return result
        
        raise ValueError(f"Неизвестная команда: {line}")
    
    @classmethod
    def parse_program(cls, program_text: str) -> List[Dict[str, Any]]:
        """
        Разбор всей программы
        
        Возвращает список команд во внутреннем представлении
        """
        commands = []
        lines = program_text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            try:
                command = cls.parse_line(line)
                if command is not None:
                    commands.append(command)
            except ValueError as e:
                raise ValueError(f"Ошибка в строке {line_num}: {e}")
            except Exception as e:
                raise ValueError(f"Ошибка в строке {line_num}: {str(e)}")
        
        return commands