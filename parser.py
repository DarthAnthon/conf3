"""
Парсер языка ассемблера УВМ
"""

import re
from typing import Dict, List, Tuple, Any
from constants import *

class Parser:
    """Парсер ассемблерных команд"""
    
    # Паттерны для разбора команд
    PATTERNS = {
        'load_const': re.compile(r'^\[\s*(?P<addr>\d+)\s*\]\s*=\s*(?P<const>-?\d+)\s*$'),
        'read_mem': re.compile(r'^\[\s*(?P<dest>\d+)\s*\]\s*=\s*\[\s*\[\s*(?P<addr>\d+)\s*\]\s*\+\s*(?P<offset>\d+)\s*\]\s*$'),
        'write_mem': re.compile(r'^\[\s*\[\s*(?P<addr>\d+)\s*\]\s*\+\s*(?P<offset>\d+)\s*\]\s*=\s*\[\s*(?P<src>\d+)\s*\]\s*$'),
        'bitreverse': re.compile(r'^\[\s*(?P<dest>\d+)\s*\]\s*=\s*bitreverse\(\s*\[\s*(?P<src>\d+)\s*\]\s*\)\s*$')
    }
    
    @classmethod
    def parse_line(cls, line: str) -> Dict[str, Any]:
        """
        Разбор строки ассемблерного кода
        
        Возвращает словарь с полями команды или None, если строка не является командой
        """
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith(';'):
            return None
        
        # Удаляем комментарии в конце строки
        if ';' in line:
            line = line.split(';')[0].strip()
        
        # Пробуем каждый паттерн
        for op_type, pattern in cls.PATTERNS.items():
            match = pattern.match(line)
            if match:
                result = {'op_type': op_type}
                result.update(match.groupdict())
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
        
        return commands