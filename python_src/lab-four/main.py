import re
import networkx as nx
import matplotlib.pyplot as plt


class CodeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_count = 0
        self.start_node = None

    def add_node(self, label):
        """Добавляет узел в граф"""
        node_id = f"N{self.node_count}"
        self.graph.add_node(node_id, label=label)
        if self.start_node is None:
            self.start_node = node_id
        self.node_count += 1
        return node_id

    def add_edge(self, from_node, to_node):
        """Добавляет направленное ребро между узлами"""
        self.graph.add_edge(from_node, to_node)

    def draw_graph(self):
        """Рисует граф управления потоком"""
        labels = nx.get_node_attributes(self.graph, "label")
        pos = nx.spring_layout(self.graph)
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            labels=labels,
            node_color="lightblue",
            edge_color="gray",
            node_size=2000,
            font_size=10,
            arrows=True,
        )
        plt.show()


def parse_cpp_to_graph(cpp_code):
    """Разбирает код C++ и создает граф"""
    lines = cpp_code.strip().split("\n")
    graph = CodeGraph()
    last_node = None
    do_block_start = None

    for line in lines:
        line = line.strip()

        if re.match(r"^do\s*{\s*$", line):
            do_node = graph.add_node("do")
            if last_node:
                graph.add_edge(last_node, do_node)
            last_node = do_block_start = do_node

        elif match := re.match(r"^\s*}\s*while\s*\((.*)\)\s*;\s*$", line):
            condition = match.group(1)
            while_node = graph.add_node(f"while ({condition})")
            graph.add_edge(last_node, while_node)
            graph.add_edge(while_node, do_block_start)
            last_node = while_node

        elif re.match(r"^\s*int\s+\w+\s*=\s*\d+\s*;\s*$", line):
            var_name, value = re.findall(
                r"\bint\s+(\w+)\s*=\s*(\d+)\s*;", line
            )[0]
            var_node = graph.add_node(f"{var_name} = {value}")
            if last_node:
                graph.add_edge(last_node, var_node)
            last_node = var_node

        elif re.match(r"^\s*\w+\s*=\s*[^;]+;\s*$", line):
            var_name, value = re.findall(r"(\w+)\s*=\s*(.*)\s*;", line)[0]
            assign_node = graph.add_node(f"{var_name} = {value}")
            if last_node:
                graph.add_edge(last_node, assign_node)
            last_node = assign_node

        elif re.match(r"^\s*\w+\+\+\s*;\s*$", line):
            var_name = re.findall(r"(\w+)\+\+;", line)[0]
            inc_node = graph.add_node(f"{var_name} += 1")
            if last_node:
                graph.add_edge(last_node, inc_node)
            last_node = inc_node

    return graph


def generate_python_from_graph(graph):
    python_code = []
    visited = set()
    stack = [(graph.start_node, 0)]

    while stack:
        node, indent_level = stack.pop()
        if node in visited:
            continue

        visited.add(node)
        label = graph.graph.nodes[node]["label"]
        indent = "    " * indent_level

        if "while (" in label:
            condition = label.replace("while (", "").replace(")", "")
            python_code.append(f"{indent}if not ({condition}):")
            python_code.append(f"{indent}    break")

        elif label == "do":
            python_code.append(f"{indent}while True:")
            indent_level += 1

        else:
            python_code.append(indent + label)

        for neighbor in graph.graph.successors(node):
            stack.append((neighbor, indent_level))

    return "\n".join(python_code)


if __name__ == "__main__":
    cpp_code = """
    int x = 0;
    do {
        x++;
    } while (x < 5);
    """

    code_graph = parse_cpp_to_graph(cpp_code)
    code_graph.draw_graph()
    python_output = generate_python_from_graph(code_graph)

    print("Python код:")
    print(python_output)
