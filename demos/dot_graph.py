import pydot

# Create the graph
graph = pydot.Dot(graph_type="digraph")
graph.set_rankdir("LR")

# Define nodes for points and elements
points = ["A", "B", "C", "D", "E", "F", "G"]
lines = ["[ A B ]", "[ E F ]"]
circles = ["( A B )", "( B A )"]

# Define ranks (columns)
points_rank = pydot.Subgraph(rank="same")
elements_rank = pydot.Subgraph(rank="same")

# Create nodes for points and add to graph
for point in points:
    node = pydot.Node(point, shape="diamond")
    graph.add_node(node)
    points_rank.add_node(node)

# Create nodes for lines and add to graph
for line in lines:
    node = pydot.Node(line, shape="box", label=f"{line}")
    graph.add_node(node)
    elements_rank.add_node(node)

# Create nodes for circles and add to graph
for circle in circles:
    node = pydot.Node(circle, shape="circle", label=f"{circle}")
    graph.add_node(node)
    elements_rank.add_node(node)

# Define edges based on the geometric constructions
# Each tuple is (from, to, label)
edges = (
    ("A", "[ A B ]", "p1"),
    ("B", "[ A B ]", "p2"),
    ("A", "( A B )", "ctr"),
    ("B", "( A B )", "rad"),
    ("[ A B ]", "C", "x"),
    ("( A B )", "C", "x"),
    ("B", "( B A )", "ctr"),
    ("A", "( B A )", "rad"),
    ("[ A B ]", "D", "x"),
    ("( B A )", "D", "x"),
    ("( A B )", "E", "x"),
    ("( B A )", "E", "x"),
    ("( A B )", "F", "x"),
    ("( B A )", "F", "x"),
    ("E", "[ E F ]", "p1"),
    ("F", "[ E F ]", "p2"),
    ("[ A B ]", "G", "x"),
    ("[ E F ]", "G", "x"),
)

# Create edges and add to graph
for edge in edges:
    graph_edge = pydot.Edge(edge[0], edge[1], label=edge[2])
    graph.add_edge(graph_edge)

# Save the graph to a file or render it
graph.write_dot("geometor_model.dot")
graph.write_png("geometor_model.png")
