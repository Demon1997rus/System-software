#include <algorithm>
#include <fstream>
#include <iostream>
#include <regex>
#include <string>
#include <vector>

#include "parser/parser.h"

std::string processCppLines(const std::string &cppCode, int indentLevel = 1,
                            char delimiter = '\n')
{
    std::string pythonCode;
    const auto lines = parser::split(cppCode, delimiter);
    for (size_t i = 0; i < lines.size(); ++i) {
        const auto &line = lines[i];
        if (parser::isIncludeDirective(line)) {
            // TODO - не знаю зачем... но пусть будет

        } else if (parser::isVariableDeclaration(line)) {
            const auto &variables = parser::parseVariableDeclaration(line);
            for (const auto &variable : variables) {
                pythonCode += parser::createAssignmentStatement(variable, indentLevel);
            }
        } else if (parser::isDoWhileLoopStart(line)) {
            int counter_do = 0;
            std::string do_while_block;
            ++i;
            while (i < lines.size() &&
                   (!parser::isDoWhileLoopEnd(lines[i]) || counter_do > 0)) {
                if (parser::isDoWhileLoopStart(lines[i])) {
                    ++counter_do;
                } else if (parser::isDoWhileLoopEnd(lines[i])) {
                    --counter_do;
                }
                do_while_block += lines[i++] + "\n";
            }
            if (i >= lines.size()) {
                throw std::runtime_error("There is no while block");
            }
            pythonCode += parser::indentPython(indentLevel);
            pythonCode += "while True:\n";
            pythonCode += processCppLines(do_while_block, indentLevel + 1);
            pythonCode += parser::indentPython(indentLevel + 1) + "if not (" +
                          parser::extractDoWhileCondition(lines[i]) + "):\n";
            pythonCode += parser::indentPython(indentLevel + 2) + "break\n";
        } else if (parser::isIncrementDecrementOperation(line)) {
            pythonCode += parser::convertIncDecToPython(line, indentLevel);
        }
    }
    return pythonCode;
}

// Функция для преобразования do-while в Python's while-True конструкцию
std::string convertCppToPython(const std::string &cppCode)
{
    std::string pythonCode;
    pythonCode += "def main():\n";
    pythonCode += processCppLines(cppCode);
    pythonCode += "\nif __name__ == \"__main__\":\n" + parser::indentPython() + "main()\n";
    return pythonCode;
}

int main()
{
    const std::string path_data = ROOT_PATH "/data/";
    const std::string path_sample = path_data + "sample.cpp";
    const std::string path_output = path_data + "output.py";

    std::ifstream inputFile(path_sample);
    std::ofstream outputFile(path_output);
    std::string code((std::istreambuf_iterator<char>(inputFile)),
                     std::istreambuf_iterator<char>());

    if (!inputFile.is_open() || !outputFile.is_open()) {
        std::cerr << "Ошибка открытия файла!" << std::endl;
        return 1;
    }

    // Преобразование do-while в код Python
    std::string pythonCode = convertCppToPython(code);
    std::cout << "---------------------------------------------------\n";
    std::cout << pythonCode << std::endl;

    // Записываем результат в выходной файл
    outputFile << pythonCode;

    inputFile.close();
    outputFile.close();

    return 0;
}
