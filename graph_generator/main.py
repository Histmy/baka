from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt

from graph_generator.dto.ToGraph import ToGraph
from graph_generator.dto.toml import Graph, PostProcessing
from graph_generator.graphs.bar import make_bar_chart
from graph_generator.graphs.box import make_box_chart
from graph_generator.graphs.histogram import make_histogram_chart
from graph_generator.graphs.line import make_line_chart
from graph_generator.graphs.pie import make_pie_chart
from graph_generator.graphs.spider import make_spider_chart
from graph_generator.loader import load_data
from graph_generator.parser import ParsedFilter, ParsedTable, load_simple_config, load_split_config
from graph_generator.post_process import PostProcess


def combine(graphs: dict[str, ToGraph], post_processing: PostProcessing) -> ToGraph:
    """
    Combines multiple data collections into one by applying the specified post-processing operation.
    Assumes `graphs` contains at least two data collections.
    """
    if post_processing.join_type is None:
        raise ValueError("Join_type must be specified for processing multiple tables.")

    match post_processing.join_type:
        case "sum":
            graphs_list = list(graphs.values())
            if post_processing.merge_serie is None:
                raise ValueError("Sum join_type requires merge_serie to specify the name of the series to sum by.")

            summed = graphs_list[0]
            for i in range(1, len(graphs_list)):
                summed = PostProcess.sum(summed, graphs_list[i], post_processing.merge_serie)
            return summed
        case "ratio":
            if len(graphs) != 2:
                raise ValueError("Ratio join_type requires exactly two tables.")

            if post_processing.merge_serie is None:
                raise ValueError("Ratio join_type requires merge_serie to specify the name of the series to divide by.")

            first, second = post_processing.ratio_first, post_processing.ratio_second
            if first is None or second is None:
                raise ValueError("Ratio join_type requires ratio_first and ratio_second to have specified the names of tables to be divided.")

            if first not in graphs or second not in graphs:
                raise ValueError(f"Specified tables for ratio not found in graphs: {first}, {second}")

            PostProcess.divide(graphs[first], graphs[second], post_processing.merge_serie)
            return graphs[first]
        case "merge":
            if post_processing.merge_serie is None:
                raise ValueError("Merge join_type requires merge_serie to specify the name of the series to merge by.")

            begined = False
            last_to_graph: Optional[ToGraph] = None
            last_name: Optional[str] = None
            for name, graph in graphs.items():
                if last_to_graph is None:
                    last_to_graph = graph
                    last_name = name
                    continue

                # in second iteration we can mark the first collection
                if not begined:
                    PostProcess.merge(last_to_graph, graph, post_processing.merge_serie, lambda x: f"({last_name}) {x}", lambda x: f"({name}) {x}")
                    begined = True
                else:
                    PostProcess.merge(last_to_graph, graph, post_processing.merge_serie, lambda x: x, lambda x: f"({name}) {x}")

            if last_to_graph is not None:
                return last_to_graph
            else:
                raise ValueError("No graphs to merge.")
        case _:
            raise ValueError(f"Unsupported join_type: {post_processing.join_type}")


def generate(tables: dict[str, ParsedTable], filters: dict[str, ParsedFilter], post_processing: Optional[PostProcessing], graph_config: Graph, path: Path) -> None:
    all: dict[str, ToGraph] = {}

    if len(tables) == 0:
        raise ValueError("No tables specified in the configuration.")

    for table_name in tables:
        output = load_data(tables[table_name], filters[table_name] if table_name in filters else ParsedFilter(row=None, column=None))

        processed = PostProcess.collapse(output)

        if post_processing is not None and post_processing.diff_serie is not None:
            processed = PostProcess.collapse(PostProcess.diff(processed, post_processing.diff_serie))
        # processed = PostProcess.simple_transpose(processed)
        all[table_name] = processed

    if len(all) == 1:
        processed = next(iter(all.values()))
    else:
        if post_processing is None:
            raise ValueError("Post-processing must be provided when multiple tables are selected.")

        processed = combine(all, post_processing)

    if post_processing is not None and post_processing.reverse is not None:
        if isinstance(post_processing.reverse, str):
            post_processing.reverse = [post_processing.reverse]

        PostProcess.reverse(processed, post_processing.reverse)

    match graph_config.type.lower():
        case "bar":
            make_bar_chart(processed, graph_config)
        case "line":
            make_line_chart(processed, graph_config)
        case "pie":
            make_pie_chart(processed, graph_config)
        case "spider":
            make_spider_chart(processed, graph_config)
        case "box":
            make_box_chart(processed, graph_config)
        case "histogram":
            make_histogram_chart(processed, graph_config)
        case _:
            raise ValueError(f"Unsupported graph type: {graph_config.type}")

    if graph_config.legend_visibility is not None:
        if graph_config.legend_visibility:
            plt.legend(loc=graph_config.legend_position if graph_config.legend_position is not None else "best")
        else:
            plt.legend().set_visible(False)

    plt.gcf().set_size_inches(graph_config.width, graph_config.height)

    if graph_config.title is not None:
        plt.title(graph_config.title)

    plt.tight_layout()
    plt.savefig(path, format="png", dpi=300)
    # plt.show()
    plt.clf()  # clear everything for next graph


def make_simple(config_file: str, output_path: Path) -> None:
    # I know about the unpack operator, but Mypy doesn't like it
    tables, filters, post_processing, graph_config = load_simple_config(config_file)
    generate(tables, filters, post_processing, graph_config, output_path)


def make_split(tables_file: str, graph_file: str, output_path: Path) -> None:
    tables, filters, post_processing, graph_config = load_split_config(tables_file, graph_file)
    generate(tables, filters, post_processing, graph_config, output_path)


# When started from command line
def main() -> None: ...


def test() -> None:
    # data = ToGraph(
    #     labels=[["A", "B", "C", "D"]],
    #     data=np.array([10, 20, 15, 5]),
    # )

    # data1 = ToGraph(
    #     labels=[["A1", "B1", "C1", "D1"], ["1st"]],
    #     data=np.array([[10], [20], [15], [5]]),
    # )

    # data2 = ToGraph(
    #     labels=[["A2", "B2", "C2", "D2"], ["2nd"]],
    #     data=np.array([[12], [22], [17], [7]]),
    # )

    # data = combine([data1, data2])

    # data = ToGraph(
    #     labels=[["A", "B", "C", "D"], ["1st", "2nd", "3rd", "4th"]],
    #     data=np.array([[10, 11, 20, 21], [15, 16, 5, 6], [12, 13, 22, 23], [17, 18, 7, 8]]),
    # )

    # make_box_chart(data)

    make_split("data/partial-tables.toml", "data/partial-graph.toml", Path("./output.png"))


if __name__ == "__main__":
    # main()
    test()
