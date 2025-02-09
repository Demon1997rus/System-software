import re


class SemanticAnalyzer:
    def __init__(self):
        self.variables = set()  # Множество объявленных переменных

    def analyze(self, code_lines):
        python_code = []

        for line in code_lines:
            line = line.strip()

            # Пропускаем пустые строки
            if not line:
                continue

            # Проверка объявления переменной
            match = re.match(r"(int|float|char|string)\s+(\w+);", line)
            if match:
                var_name = match.group(2)
                if var_name in self.variables:
                    print(f"Ошибка: Повторное объявление переменной '{var_name}'")
                else:
                    self.variables.add(var_name)
                continue  # В Python явное объявление не нужно

            # Присваивание переменной значения
            match = re.match(r"(\w+)\s*=\s*(.+);", line)
            if match:
                var_name, value = match.groups()
                if var_name not in self.variables:
                    print(
                        f"Ошибка: Использование необъявленной переменной '{var_name}'"
                    )
                else:
                    python_code.append(f"{var_name} = {value}")
                continue

            # Инкремент (x++)
            match = re.match(r"(\w+)\+\+;", line)
            if match:
                var_name = match.group(1)
                if var_name not in self.variables:
                    print(
                        f"Ошибка: Использование необъявленной переменной '{var_name}'"
                    )
                else:
                    python_code.append(f"{var_name} += 1")
                continue

            # Цикл do ... while
            if line.startswith("do {"):
                python_code.append("while True:  # do-while loop")
                continue
            if line.startswith("} while ("):
                condition = re.search(r"\((.+)\);", line).group(1)
                python_code.append(f"    if not ({condition}): break")
                continue

            print(f"Ошибка: Неподдерживаемая конструкция '{line}'")

        return "\n".join(python_code)


# Тестовый пример кода C++
cpp_code = """
int x;
x = 10;
x++;
do {
    x++;
} while (x < 15);
"""

cpp_lines = cpp_code.strip().split("\n")
analyzer = SemanticAnalyzer()
python_code = analyzer.analyze(cpp_lines)

print("\nРезультат трансляции в Python:")
print(python_code)
