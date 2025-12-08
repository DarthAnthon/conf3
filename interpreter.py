"""
Интерпретатор для Учебной Виртуальной Машины (УВМ)
"""

from typing import List
from constants import *

class UVMInterpreter:
    """Интерпретатор УВМ"""
    
    def __init__(self, memory_size: int = 65536):
        self.memory = [0] * memory_size
        self.pc = 0  # Программный счетчик
        
    def bitreverse_16(self, value: int) -> int:
        """Обращение битов 16-битного числа"""
        result = 0
        for i in range(16):
            if value & (1 << i):
                result |= 1 << (15 - i)
        return result & BITREVERSE_MASK
    
    def extract_fields(self, command_bytes: bytes) -> dict:
        """Извлечение полей из 7 байт команды"""
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
    
    def execute_command(self, command_bytes: bytes) -> bool:
        """Выполнение одной команды"""
        fields = self.extract_fields(command_bytes)
        opcode = fields['A']
        
        if opcode == OP_LOAD_CONST:
            # Загрузка константы
            addr = fields['B']
            const = fields['C']
            # Преобразование из дополнительного кода
            if const & (1 << (FIELD_SIZES['C'] - 1)):
                const = const - (1 << FIELD_SIZES['C'])
            self.memory[addr] = const
            
        elif opcode == OP_READ_MEM:
            # Чтение из памяти
            offset = fields['B']
            addr_ptr = fields['C']
            dest = fields['D']
            
            # Вычисляем адрес: значение по адресу addr_ptr + offset
            base_addr = self.memory[addr_ptr]
            src_addr = base_addr + offset
            self.memory[dest] = self.memory[src_addr]
            
        elif opcode == OP_WRITE_MEM:
            # Запись в память
            src = fields['B']
            addr_ptr = fields['C']
            offset = fields['D']
            
            # Вычисляем адрес назначения: значение по адресу addr_ptr + offset
            base_addr = self.memory[addr_ptr]
            dest_addr = base_addr + offset
            self.memory[dest_addr] = self.memory[src]
            
        elif opcode == OP_BITREVERSE:
            # Обращение битов
            src = fields['B']
            dest_ptr = fields['C']
            
            # Получаем значение, обращаем биты, записываем
            value = self.memory[src]
            reversed_value = self.bitreverse_16(value)
            self.memory[self.memory[dest_ptr]] = reversed_value
            
        else:
            raise ValueError(f"Неизвестный код операции: {opcode}")
        
        return True
    
    def load_program(self, binary_data: bytes):
        """Загрузка программы в память"""
        # В УВМ программа хранится отдельно от данных
        # Для простоты будем считать, что программа начинается с адреса 0
        program_size = len(binary_data)
        if program_size % 7 != 0:
            raise ValueError("Размер программы должен быть кратен 7 байтам")
        
        self.program = []
        for i in range(0, program_size, 7):
            self.program.append(binary_data[i:i+7])
    
    def run(self):
        """Запуск интерпретатора"""
        self.pc = 0
        while self.pc < len(self.program):
            command = self.program[self.pc]
            self.execute_command(command)
            self.pc += 1


def test_specification():
    """Тесты из спецификации УВМ"""
    
    # Тест 1: Загрузка константы
    print("=== Тест 1: Загрузка константы ===")
    assembler = Assembler()
    
    # Ассемблируем тестовую команду
    test1_cmd = {'op_type': 'load_const', 'addr': '201', 'const': '567'}
    fields = assembler.assemble_command(test1_cmd)
    binary = assembler.pack_command(fields)
    
    print(f"Ожидаемые байты: 0xD1, 0x64, 0xC0, 0x8D, 0x00, 0x00, 0x00")
    print(f"Полученные байты: {', '.join(f'0x{b:02X}' for b in binary)}")
    assert list(binary) == [0xD1, 0x64, 0xC0, 0x8D, 0x00, 0x00, 0x00]
    print("✓ Тест 1 пройден\n")
    
    # Тест 2: Чтение из памяти
    print("=== Тест 2: Чтение из памяти ===")
    test2_cmd = {'op_type': 'read_mem', 'dest': '386', 'addr': '962', 'offset': '21'}
    fields = assembler.assemble_command(test2_cmd)
    binary = assembler.pack_command(fields)
    
    print(f"Ожидаемые байты: 0xAA, 0x0A, 0x08, 0x0F, 0x04, 0x03, 0x00")
    print(f"Полученные байты: {', '.join(f'0x{b:02X}' for b in binary)}")
    assert list(binary) == [0xAA, 0x0A, 0x08, 0x0F, 0x04, 0x03, 0x00]
    print("✓ Тест 2 пройден\n")
    
    # Тест 3: Запись в память
    print("=== Тест 3: Запись в память ===")
    test3_cmd = {'op_type': 'write_mem', 'src': '217', 'addr': '226', 'offset': '54'}
    fields = assembler.assemble_command(test3_cmd)
    binary = assembler.pack_command(fields)
    
    print(f"Ожидаемые байты: 0xEC, 0x6C, 0x80, 0x38, 0xC0, 0x06, 0x00")
    print(f"Полученные байты: {', '.join(f'0x{b:02X}' for b in binary)}")
    assert list(binary) == [0xEC, 0x6C, 0x80, 0x38, 0xC0, 0x06, 0x00]
    print("✓ Тест 3 пройден\n")
    
    # Тест 4: Обращение битов
    print("=== Тест 4: Обращение битов ===")
    test4_cmd = {'op_type': 'bitreverse', 'dest': '735', 'src': '980'}
    fields = assembler.assemble_command(test4_cmd)
    binary = assembler.pack_command(fields)
    
    print(f"Ожидаемые байты: 0x35, 0xEA, 0xC1, 0xB7, 0x00, 0x00, 0x00")
    print(f"Полученные байты: {', '.join(f'0x{b:02X}' for b in binary)}")
    assert list(binary) == [0x35, 0xEA, 0xC1, 0xB7, 0x00, 0x00, 0x00]
    print("✓ Тест 4 пройден\n")
    
    print("Все тесты из спецификации пройдены успешно!")


if __name__ == '__main__':
    # Запуск тестов
    from assembler import Assembler
    test_specification()