import pathlib
import tomllib

from recommendations import recommendation_ids


ROOT = pathlib.Path(__file__).parents[1]


def test_searches_repository_names_and_descriptions():
    with (ROOT / "config.toml").open("rb") as config_file:
        config = tomllib.load(config_file)

    assert config["recommend"]["search"]["columns"] == [
        "item.ItemId",
        "item.Comment",
    ]


def test_uses_pygorse_with_search_items_support():
    requirements = (ROOT / "requirements.txt").read_text().splitlines()

    assert "PyGorse==0.5.1" in requirements


def test_web_image_includes_recommendation_helpers():
    dockerfile = (ROOT / "docker" / "web" / "Dockerfile").read_text()

    assert "COPY app.py jobs.py gunicorn.conf.py recommendations.py utils.py ./" in dockerfile


def test_extracts_item_ids_from_scored_recommendations():
    class Score:
        def __init__(self, item_id):
            self.id = item_id

    assert recommendation_ids([Score("gorse-io:gorse"), Score("gorse-io:gitrec")]) == [
        "gorse-io:gorse",
        "gorse-io:gitrec",
    ]
