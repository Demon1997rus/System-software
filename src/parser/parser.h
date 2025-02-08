#pragma once

#include <regex>
#include <string>
#include <vector>

#include "structs.h"

namespace parser {
bool isVariableDeclaration(const std::string &line);

bool isIncrementDecrementOperation(const std::string &line);

bool isIncludeDirective(const std::string &line);

bool isDoWhileLoopStart(const std::string &line);

bool isDoWhileLoopEnd(const std::string &line);

std::vector<std::string> split(const std::string &input, char delimiter);

std::vector<VariableInfo> parseVariableDeclaration(const std::string &input);

std::string mapToPythonType(const std::string &cppType);

std::string indentPython(int indentLevel = 1);

std::string createAssignmentStatement(const VariableInfo &info, int indentLevel = 0);

std::string convertIncDecToPython(const std::string &cppLine, int indentLevel = 0);

std::string extractDoWhileCondition(const std::string &line);
}
