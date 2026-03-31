import numpy as np

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Filter, Graph
from graph_generator.graphs.bar import make_bar_chart
from graph_generator.graphs.box import make_box_chart
from graph_generator.graphs.histogram import make_histogram_chart
from graph_generator.graphs.line import make_line_chart
from graph_generator.graphs.pie import make_pie_chart
from graph_generator.graphs.spider import make_spider_chart
from graph_generator.loader import load_data
from graph_generator.parser import ParsedTable, load_simple_config, load_split_config
from graph_generator.post_process import collapse


def generate(tables: dict[str, ParsedTable], filters: dict[str, Filter], post_processing: dict, graph_config: Graph) -> None:
    all = []

    if len(tables) == 0:
        raise ValueError("No tables specified in the configuration.")

    for table_name in tables:
        vystup = load_data(tables[table_name], filters[table_name])

        processed = collapse(vystup)
        # processed = simple_transpose(processed)
        all.append(processed)

    processed = all[0]

    match graph_config.type.lower():
        case "bar":
            make_bar_chart(processed)
        case "line":
            make_line_chart(processed)
        case "pie":
            make_pie_chart(processed)
        case "spider":
            make_spider_chart(processed, graph_config)
        case "box":
            make_box_chart(processed)
        case "histogram":
            make_histogram_chart(processed)
        case _:
            raise ValueError(f"Unsupported graph type: {graph_config.type}")


def make_simple(config_file: str) -> None:
    generate(*load_simple_config(config_file))


def make_split(tables_file: str, graph_file: str) -> None:
    generate(*load_split_config(tables_file, graph_file))


# When started from command line
def main() -> None: ...


def test() -> None:
    data = ToGraph(
        labels=[["A", "B", "C", "D"]],
        data=np.array([10, 20, 15, 5]),
    )

    data = ToGraph(
        labels=[["A", "B", "C", "D"], ["1st", "2nd"]],
        data=np.array([[10, 11], [20, 21], [15, 16], [5, 6]]),
    )

    # data = ToGraph(
    #     labels=[["A", "B", "C", "D"], ["1st", "2nd"], ["T1", "T2"]],
    #     data=np.array([[[10, 11], [20, 21]], [[15, 16], [5, 6]], [[12, 13], [22, 23]], [[17, 18], [7, 8]]]),
    # )

    make_spider_chart(data, Graph(title="Test", type="Pie", width=6, height=4))


if __name__ == "__main__":
    main()
    # test()
