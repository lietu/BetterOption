"""
This script expects to be run from the repository root
"""

import os
from pathlib import Path
import shutil

import frontmatter
import yaml

REPOSITORY_BASE = "https://github.com/lietu/BetterOption/tree/master/"


class Classifier:
    def __init__(self):
        self.categories = {}
        self.classes = {}
        self.options = {}
        self.problems = {}
        self.things = {}

    def run(self, src, dst):
        self.classes = self._load_files(src / "problems" / "classes")
        self.categories = self._load_files(src / "things" / "categories")
        self.options = self._load_files(src / "options")
        self.problems = self._load_problems(src / "problems")
        self.things = self._load_things(src / "things")

        self.generate_data()
        self.write_data(dst)

    def _load_files(self, path, validator=None):
        data = {}
        for entry in path.iterdir():
            if entry.is_dir():
                continue

            item = frontmatter.load(entry)
            if validator:
                try:
                    validator(item)
                except Exception as e:
                    raise ValueError(f"{entry} failed validation: {e}")

            name = entry.parts[-1].rsplit(".", 1)[0]
            item.metadata["raw_name"] = name
            item.metadata["source_uri"] = REPOSITORY_BASE + entry.as_posix()
            data[name] = item

        return data

    def _load_problems(self, path):
        def _validator(item):
            cls = item.metadata["class"]
            if cls not in self.classes:
                raise ValueError(f"Class {cls} not found.")

            return True

        return self._load_files(path, _validator)

    def _load_things(self, path):
        def _validator(item):
            cat = item.metadata["category"]
            if cat not in self.categories:
                raise ValueError(f"Category {cat} not found.")

            for opt in item.metadata["options"]:
                name = opt["name"]
                if name not in self.options:
                    raise ValueError(f"Option {name} not found.")

            return True

        return self._load_files(path, _validator)

    def _get_definition(self, type_, name):
        if type_ == "class":
            class_ = self.classes[name].metadata
            return {
                "raw_name": class_["raw_name"],
                "item_name": class_["item_name"],
                "path": f"classes/{name}.html"
            }

        if type_ == "category":
            category = self.categories[name].metadata
            return {
                "raw_name": category["raw_name"],
                "item_name": category["item_name"],
                "path": f"categories/{name}.html"
            }

        if type_ == "option":
            option = self.options[name].metadata
            return {
                "raw_name": option["raw_name"],
                "item_name": option["item_name"],
                "path": f"options/{name}.html"
            }

        if type_ == "problem":
            problem = self.problems[name].metadata
            class_ = problem["class"]["raw_name"]
            return {
                "raw_name": problem["raw_name"],
                "item_name": problem["item_name"],
                "class_path": f"classes/{class_}.html",
                "class_name": self.classes[class_].metadata["item_name"],
                "path": f"problems/{name}.html"
            }

        if type_ == "thing":
            thing = self.things[name].metadata
            category = thing["category"]["raw_name"]
            return {
                "raw_name": thing["raw_name"],
                "item_name": thing["item_name"],
                "category_path": f"categories/{category}.html",
                "category_name": self.categories[category].metadata[
                    "item_name"],
                "path": f"things/{name}.html"
            }

        raise ValueError(f"Unsupported definition type {type_}")

    def _add_meta(self, item, target_type, target):
        if target_type == "problem":
            field = "problems"
        elif target_type == "thing":
            field = "things"
        elif target_type == "category":
            field = "categories"
        elif target_type == "class":
            field = "classes"
        elif target_type == "option":
            field = "options"
        else:
            raise ValueError(f"Unsupported target type {target_type}")

        values = item.metadata.get(field, [])
        values.append(self._get_definition(target_type, target))

        item.metadata[field] = list({
                                        value["raw_name"]: value for value in
                                        values
                                    }.values())

    def generate_data(self):
        for problem, item in self.problems.items():
            item.metadata["layout"] = "problem"
            item.metadata["title"] = item.metadata["item_name"]
            class_ = item.metadata["class"]
            item.metadata["class"] = self._get_definition("class", class_)
            self._add_meta(self.classes[class_], "problem", problem)

        for thing, item in self.things.items():
            item.metadata["layout"] = "thing"
            item.metadata["title"] = item.metadata["item_name"]
            category = item.metadata["category"]
            item.metadata["category"] = self._get_definition("category",
                                                             category)
            self._add_meta(self.categories[category], "thing", thing)

            o = []
            for option in item.metadata["options"]:
                option_name = option["name"]
                new_opt = self._get_definition("option", option_name)
                new_opt["description"] = option["description"]
                o.append(new_opt)
                self._add_meta(self.options[option_name], "thing", thing)
            item.metadata["options"] = o

            p = []
            for problem in item.metadata["problems"]:
                p.append(self._get_definition("problem", problem))
                self._add_meta(self.problems[problem], "thing", thing)

                for option in item.metadata["options"]:
                    option_name = option["raw_name"]
                    self._add_meta(self.problems[problem], "option", option_name)
                    self._add_meta(self.options[option_name], "problem",
                                   problem)
            item.metadata["problems"] = p

        for category, item in self.categories.items():
            item.metadata["layout"] = "category"
            item.metadata["title"] = item.metadata["item_name"]

        for class_, item in self.classes.items():
            item.metadata["layout"] = "class"
            item.metadata["title"] = item.metadata["item_name"]

        for class_, item in self.options.items():
            item.metadata["layout"] = "option"
            item.metadata["title"] = item.metadata["item_name"]

    def write_data(self, dst):
        classes_dir = dst / "classes"
        categories_dir = dst / "categories"
        problems_dir = dst / "problems"
        things_dir = dst / "things"
        options_dir = dst / "options"
        data_dir = dst / "_data"

        paths = (
            classes_dir,
            categories_dir,
            problems_dir,
            things_dir,
            options_dir,
            data_dir
        )

        for path in paths:
            if path.exists():
                shutil.rmtree(path)
            path.mkdir()

        classes = []
        for name, item in self.classes.items():
            (classes_dir / f"{name}.md").write_text(frontmatter.dumps(item))
            classes.append(self._get_definition("class", name))

        categories = []
        for name, item in self.categories.items():
            (categories_dir / f"{name}.md").write_text(frontmatter.dumps(item))
            categories.append(self._get_definition("category", name))

        problems = []
        for name, item in self.problems.items():
            (problems_dir / f"{name}.md").write_text(frontmatter.dumps(item))
            problems.append(self._get_definition("problem", name))

        things = []
        for name, item in self.things.items():
            (things_dir / f"{name}.md").write_text(frontmatter.dumps(item))
            things.append(self._get_definition("thing", name))

        options = []
        for name, item in self.options.items():
            (options_dir / f"{name}.md").write_text(frontmatter.dumps(item))
            options.append(self._get_definition("option", name))

        (data_dir / "classes.yml").write_text(yaml.dump(classes))
        (data_dir / "categories.yml").write_text(yaml.dump(categories))
        (data_dir / "problems.yml").write_text(yaml.dump(problems))
        (data_dir / "things.yml").write_text(yaml.dump(things))
        (data_dir / "options.yml").write_text(yaml.dump(options))


def main():
    if not Path("Gemfile").exists():
        os.chdir("..")

    src = Path(".")
    dst = Path("web")

    c = Classifier()
    c.run(src, dst)


if __name__ == "__main__":
    main()
