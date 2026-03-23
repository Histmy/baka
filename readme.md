# Automated Creation of Informatics Europe Data Reports

This repository will contain the code and documentation for the bachelor thesis project focused on the automated creation of graphs from configuration file and data files with a GUI also allowing to embed those graphs in a Word document. The project is intended for use by Informatics Europe, but may be adapted for use by anyone.

## Project Overview

Currently, only a prototype of a graphic generation tool is available. It lives in a `graph_generator` directory. To run it, it is first necessary to install the required dependencies, which can be done using pip:

```bash
pip install -r requirements.txt
```

After installing the dependencies, you can run the prototype using the following command from the root directory of the project:

```bash
python -m graph_generator.main
```
