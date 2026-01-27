SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"




uv run $SCRIPT_DIR/../../blogged/manage.py graph_models --pygraphviz -a --app-style $SCRIPT_DIR/style.json -o $SCRIPT_DIR/eco_blog_models.png -v 3
uv run $SCRIPT_DIR/../../blogged/manage.py graph_models --pydot -a --app-style $SCRIPT_DIR/style.json -o $SCRIPT_DIR/eco_blog_models.dot -v 3