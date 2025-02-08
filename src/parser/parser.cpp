#include "parser.h"

#include <unordered_map>

#include <boost/algorithm/string.hpp>

namespace parser {
bool isVariableDeclaration(const std::string &line)
{
    std::regex variableDeclarationPattern(
        R"((const\s+)?(unsigned\s+|signed\s+)?\b(int|double|float|char|bool|long|short|std::string)\b\s+[\w_]+(\s*=\s*[^;]+)?(;|\s*,\s*[\w_]+(\s*=\s*[^;]+)?)+)");
    return std::regex_search(line, variableDeclarationPattern);
}

bool isIncrementDecrementOperation(const std::string &line)
{
    std::regex incDecPattern(R"((\+\+|\-\-)\s*\b\w+\b|\b\w+\b\s*(\+\+|\-\-))");
    return std::regex_search(line, incDecPattern);
}

bool isIncludeDirective(const std::string &line)
{
    std::string trimmed = line;
    boost::algorithm::trim(trimmed);
    std::regex includePattern(R"(^#include\s*<.*?>$|^#include\s*".*?"$)");
    return std::regex_match(trimmed, includePattern);
}

bool isDoWhileLoopStart(const std::string &line)
{
    std::string trimmed = line;
    boost::algorithm::trim(trimmed);
    std::regex doPattern(R"(^\s*do\s*\{?)");
    return std::regex_search(trimmed, doPattern);
}

bool isDoWhileLoopEnd(const std::string &line)
{
    std::string trimmed = line;
    boost::algorithm::trim(trimmed);
    std::regex whilePattern(R"(while\s*\(.*?\)\s*;)");
    return std::regex_search(trimmed, whilePattern);
}

std::vector<std::string> split(const std::string &input, char delimiter)
{
    std::vector<std::string> results;
    boost::algorithm::split(results, input, boost::is_any_of(std::string(1, delimiter)));
    return results;
}

std::vector<VariableInfo> parseVariableDeclaration(const std::string &input)
{
    std::vector<VariableInfo> variables;

    // Копируем входную строку для работы с ней
    std::string line = input;

    // Удаляем начальные и конечные пробелы и точку с запятой
    boost::algorithm::trim(line);
    boost::algorithm::trim_if(line, boost::is_any_of(";"));

    // Выделяем первую часть строки (тип переменных)
    size_t firstSpace = line.find(' ');
    if (firstSpace == std::string::npos) {
        return variables;
    }

    std::string type = line.substr(0, firstSpace);
    std::string rest = line.substr(firstSpace + 1);

    // Разделяем оставшуюся часть строки по запятым
    std::vector<std::string> declarations;
    boost::algorithm::split(declarations, rest, boost::is_any_of(","),
                            boost::token_compress_on);

    // Обработаем каждую переменную
    for (auto &decl : declarations) {
        boost::algorithm::trim(decl);

        // Разбиваем каждую часть на имя и значение
        std::vector<std::string> parts;
        boost::algorithm::split(parts, decl, boost::is_any_of("="), boost::token_compress_on);

        if (parts.size() >= 1) {
            VariableInfo varInfo;
            varInfo.type = type;
            varInfo.name = parts[0];
            boost::algorithm::trim(varInfo.name);

            if (parts.size() == 2) {
                varInfo.value = parts[1];
                boost::algorithm::trim(varInfo.value);
            }

            variables.push_back(varInfo);
        }
    }

    return variables;
}

std::string mapToPythonType(const std::string &cppType)
{
    // Определяем статическое отображение C++ типов на Python
    static const std::unordered_map<std::string, std::string> typeMap = {
        {"int", "int"},   {"double", "float"},    {"float", "float"},
        {"char", "str"},  {"bool", "bool"},       {"long", "int"},
        {"short", "int"}, {"std::string", "str"}, {"string", "str"}};

    // Ищем соответствие для данного типа
    auto it = typeMap.find(cppType);
    if (it != typeMap.end()) {
        return it->second;
    } else {
        throw std::runtime_error("Unknown type");
    }
}

std::string indentPython(int indentLevel)
{
    return std::string(indentLevel * 4, ' ');
}

std::string createAssignmentStatement(const VariableInfo &info, int indentLevel)
{
    std::string res;
    res += indentPython(indentLevel);
    res += info.name;
    res += " = ";
    if (info.value.empty()) {
        res += mapToPythonType(info.type);
        res += "()";
    } else {
        res += info.value;
    }
    res += '\n';
    return res;
}

// Конвертационная функция для инкрементации и декрементации
std::string convertIncDecToPython(const std::string &cppLine, int indentLevel)
{
    std::string temp = cppLine;
    boost::trim(temp);
    std::regex preIncPattern(R"(\+\+\s*(\b\w+\b))");
    std::regex postIncPattern(R"((\b\w+\b)\s*\+\+)");
    std::regex preDecPattern(R"(\-\-\s*(\b\w+\b))");
    std::regex postDecPattern(R"((\b\w+\b)\s*\-\-)");

    temp = std::regex_replace(temp, preIncPattern, "$1 += 1");
    temp = std::regex_replace(temp, postIncPattern, "$1 += 1");
    temp = std::regex_replace(temp, preDecPattern, "$1 -= 1");
    temp = std::regex_replace(temp, postDecPattern, "$1 -= 1");

    std::string result = indentPython(indentLevel);
    result.reserve(result.size() + temp.size() + 1);
    result += temp;
    result += '\n';

    return result;
}

std::string extractDoWhileCondition(const std::string &line)
{
    std::string trimmed = line;
    boost::algorithm::trim(trimmed);

    // Регулярное выражение ищет окончание do-while и извлекает условие
    std::regex whilePattern(R"(while\s*\((.*?)\)\s*;)");
    std::smatch match;

    if (std::regex_search(trimmed, match, whilePattern) && match.size() > 1) {
        return match.str(1);
    } else {
        throw std::runtime_error("There is no condition in the while loop");
    }
}

}
