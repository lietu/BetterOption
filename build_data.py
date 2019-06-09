"""
This script expects to be run from the repository root
"""

import os
import shutil
from pathlib import Path

import frontmatter
import yaml

REPOSITORY_BASE = "https://github.com/lietu/BetterOption/tree/master/"


class Item:
    FILE_PATH = None
    LAYOUT = None

    def __init__(self, classifier, path, item):
        self.classifier = classifier  # type: Classifier
        self.path = path  # type: Path
        self.item = item  # type: frontmatter.Post

        self.raw_name = path.parts[-1].rsplit(".", 1)[0]
        self.item_name = self.get_meta("item_name")

        if not self.LAYOUT:
            raise ValueError("Direct use of Item")

        self.set_meta("layout", self.LAYOUT)
        self.set_meta("title", self.item_name)
        self.set_meta("image", self.get_image())
        self.set_meta("source_uri", REPOSITORY_BASE + path.as_posix())

    def get_image(self):
        return self.get_meta("image", "none")

    def get_meta(self, field, default=None):
        return self.item.metadata.get(field, default)

    def set_meta(self, field, value):
        self.item.metadata[field] = value

    def add_meta(self, field, value):
        values = self.get_meta(field, [])
        values.append(value)

        # Filter to unique values only
        values = list({
                          value["raw_name"]: value for value in values
                      }.values())

        self.set_meta(field, values)

    def get_definition(self):
        raise ValueError("Called get_definition on Item")

    def generate_data(self):
        raise ValueError("Called generate_data on Item")

    def validator(self):
        image = self.get_meta("image", None)
        if image:
            if image not in self.classifier.images:
                raise ValueError(f"Invalid image {image}")

    def get_link(self):
        if not self.FILE_PATH:
            raise ValueError("No FILE_PATH defined!")

        return f"{self.FILE_PATH}/{self.raw_name}.html"

    def get_path(self):
        if not self.FILE_PATH:
            raise ValueError("No FILE_PATH defined!")

        return f"{self.FILE_PATH}/{self.raw_name}.html"


class Category(Item):
    FILE_PATH = "categories"
    LAYOUT = "category"

    def __init__(self, classifier, path, item):
        super().__init__(classifier, path, item)

    def generate_data(self):
        pass

    def get_definition(self):
        return {
            "raw_name": self.raw_name,
            "item_name": self.item_name,
            "link": self.get_link(),
            "image": self.get_image()
        }


class Class(Item):
    FILE_PATH = "classes"
    LAYOUT = "class"

    def __init__(self, classifier, path, item):
        super().__init__(classifier, path, item)

    def generate_data(self):
        pass

    def get_definition(self):
        return {
            "raw_name": self.raw_name,
            "item_name": self.item_name,
            "link": self.get_link(),
            "image": self.get_image()
        }


class Problem(Item):
    FILE_PATH = "problems"
    LAYOUT = "problem"

    def __init__(self, classifier, path, item):
        super().__init__(classifier, path, item)
        self.cls = self.get_meta("class")

    def validator(self):
        if self.cls not in self.classifier.classes:
            raise ValueError(f"Class {self.cls} not found.")

        super().validator()

    def get_class(self) -> Class:
        return self.classifier.classes[self.cls]

    def get_definition(self):
        class_ = self.get_class()
        return {
            "raw_name": self.raw_name,
            "item_name": self.item_name,
            "class_link": f"classes/{class_.raw_name}.html",
            "class_name": class_.item_name,
            "link": self.get_link(),
            "image": self.get_image()
        }

    def generate_data(self):
        self.set_meta("class", self.get_class().get_definition())
        self.get_class().add_meta("problems", self.get_definition())


class Thing(Item):
    FILE_PATH = "things"
    LAYOUT = "thing"

    def __init__(self, classifier, path, item):
        super().__init__(classifier, path, item)
        self.category = self.get_meta("category")

    def validator(self):
        if self.category not in self.classifier.categories:
            raise ValueError(f"Category {self.category} not found.")

        super().validator()

    def get_category(self) -> Category:
        return self.classifier.categories[self.category]

    def get_link(self):
        return f"/{self.raw_name}/"

    def generate_data(self):
        self.set_meta("permalink", self.get_link())
        self.set_meta("category", self.get_category().get_definition())

        definition = self.get_definition()
        print(f"Linking {self.raw_name} in category {self.category}")
        self.get_category().add_meta("things", definition)

        o = []
        for option_item in self.get_meta("options", []):
            option_name = option_item["raw_name"]
            option = self.classifier.things[option_name]  # type: Thing

            new_opt = option.get_definition()
            new_opt["description"] = option_item["description"]

            o.append(new_opt)

            print(f"Linking {option_name} as an option for {self.raw_name}")
            option.add_meta("option_for", definition)
        self.set_meta("options", o)

        p = []
        for problem_name in self.get_meta("problems", []):
            problem = self.classifier.problems[problem_name]
            problem_definition = problem.get_definition()
            p.append(problem_definition)

            print(f"Linking {self.raw_name} under problem {problem_name}")
            problem.add_meta("things", definition)

            print(f"Linking {self.raw_name} under problem class {problem.cls}")
            problem.get_class().add_meta("things", definition)

            for option_item in self.get_meta("options"):
                option_name = option_item["raw_name"]
                option = self.classifier.things[option_name]

                print(f"Linking {option_name} as an option for "
                      f"problem {problem_name}")
                problem.add_meta("options", option.get_definition())
                option.add_meta("option_for_problem", problem_definition)
        self.set_meta("problems", p)

    def get_definition(self):
        category = self.get_category()
        return {
            "raw_name": self.raw_name,
            "item_name": self.item_name,
            "category_link": f"categories/{category.raw_name}.html",
            "category_name": category.item_name,
            "link": f"/{self.raw_name}/",
            "image": self.get_image()
        }


class Classifier:
    def __init__(self):
        self.categories = {}  # type: dict[Category]
        self.classes = {}  # type: dict[Class]
        self.problems = {}  # type: dict[Problem]
        self.things = {}  # type: dict[Thing]
        self.images = {}  # type: dict[dict]

    def run(self, src, dst):
        self.images = self._load_images(src / "images")

        self.classes = self._load_files(
            src / "problems" / "classes",
            cls=Class
        )
        self.categories = self._load_files(
            src / "things" / "categories",
            cls=Category
        )
        self.problems = self._load_files(
            src / "problems",
            cls=Problem
        )
        self.things = self._load_files(
            src / "things",
            cls=Thing
        )

        self.generate_data()
        self.write_data(dst)

    @staticmethod
    def _load_images(path):
        data = {}
        for entry in path.iterdir():
            filename = entry.parts[-1]
            if not filename.endswith(".md"):
                continue

            doc = frontmatter.load(entry)

            name = filename.rsplit(".", 1)[0]
            source_file = doc.metadata["filename"]
            data[name] = {
                "source": doc.metadata["source"],
                "content": doc.content,
                "filename": source_file,
                "license": doc.metadata["license"],
                "url": (path / source_file).as_posix()
            }
        return data

    def _load_files(self, path, cls):
        data = {}
        for entry in path.iterdir():
            if entry.is_dir():
                continue

            doc = frontmatter.load(entry)
            item = cls(self, entry, doc)
            try:
                item.validator()
            except Exception as e:
                raise ValueError(f"{entry} failed validation: {e}")

            data[item.raw_name] = item

        return data

    def get_definition(self, type_, name):
        if type_ == "class":
            return self.classes[name].get_definition()
        elif type_ == "category":
            return self.categories[name].get_definition()
        elif type_ == "problem":
            return self.problems[name].get_definition()
        elif type_ == "thing":
            return self.things[name].get_definition()

        raise ValueError(f"Unsupported definition type {type_}")

    def generate_data(self):
        for _, problem in self.problems.items():
            problem.generate_data()

        for _, thing in self.things.items():
            thing.generate_data()

        for _, category in self.categories.items():
            category.generate_data()

        for _, cls in self.classes.items():
            cls.generate_data()

    def write_data(self, dst):
        classes_dir = dst / Class.FILE_PATH
        categories_dir = dst / Category.FILE_PATH
        problems_dir = dst / Problem.FILE_PATH
        things_dir = dst / Thing.FILE_PATH
        images_dir = dst / "images"
        data_dir = dst / "_data"

        paths = (
            classes_dir,
            categories_dir,
            problems_dir,
            things_dir,
            images_dir,
            data_dir
        )

        for path in paths:
            if path.exists():
                shutil.rmtree(path)
            path.mkdir()

        classes = []
        for _, cls in self.classes.items():
            path = (dst / cls.get_path())
            path.write_text(frontmatter.dumps(cls.item))
            classes.append(cls.get_definition())

        categories = []
        for _, cat in self.categories.items():
            path = (dst / cat.get_path())
            path.write_text(frontmatter.dumps(cat.item))
            categories.append(cat.get_definition())

        problems = []
        for _, prob in self.problems.items():
            path = (dst / prob.get_path())
            path.write_text(frontmatter.dumps(prob.item))
            problems.append(prob.get_definition())

        things = []
        for _, thing in self.things.items():
            path = (dst / thing.get_path())
            path.write_text(frontmatter.dumps(thing.item))
            things.append(thing.get_definition())

        for _, image in self.images.items():
            shutil.copy(image["url"], images_dir / image["filename"])
            del image["filename"]

        (data_dir / "classes.yml").write_text(yaml.dump(classes))
        (data_dir / "categories.yml").write_text(yaml.dump(categories))
        (data_dir / "problems.yml").write_text(yaml.dump(problems))
        (data_dir / "things.yml").write_text(yaml.dump(things))
        (data_dir / "images.yml").write_text(yaml.dump(self.images))


def main():
    if not Path("Gemfile").exists():
        os.chdir("..")

    src = Path(".")
    dst = Path("web")

    c = Classifier()
    c.run(src, dst)


if __name__ == "__main__":
    main()
