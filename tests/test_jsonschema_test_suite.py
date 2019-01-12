import json
import os
import subprocess
import textwrap
import unittest

import jsonschemax

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE_PATH = os.path.join(ROOT_PATH, "tests", "JSON-Schema-Test-Suite")


def run(cmd, check=True, shell=True):
    subprocess.run(cmd, check=check, shell=shell)


def download_suite():
    if not os.path.isdir(SUITE_PATH):
        run(
            "git clone https://github.com/json-schema-org/JSON-Schema-Test-Suite.git "
            + SUITE_PATH
        )


def load_jsons(version):
    assert isinstance(version, str) and version.startswith("draft")

    draft7dir = os.path.join(SUITE_PATH, "tests", version)  # not include optional json

    for filename in os.listdir(draft7dir):
        if filename.endswith("json"):
            json_path = os.path.join(draft7dir, filename)
            with open(json_path) as f:
                yield json_path, json.loads(f.read())


def load_remote_schemas():
    remotes_dir_path = os.path.join(SUITE_PATH, "remotes")
    for (dirpath, dirnames, filenames) in os.walk(remotes_dir_path):
        for filename in filenames:
            json_file_path = os.path.join(dirpath, filename)
            with open(json_file_path) as f:
                yield (
                    os.path.relpath(json_file_path, remotes_dir_path),
                    json.loads(f.read()),
                )


def get_tests(version):
    for filepath, group_list in load_jsons(version):
        for group in group_list:
            schema = group["schema"]
            for test in group["tests"]:
                instance = test["data"]
                is_valid = test["valid"]
                yield (
                    filepath,
                    group["description"],
                    test["description"],
                    schema,
                    instance,
                    is_valid,
                )


def get_remote_schemas():
    remote_schemas = {
        "http://localhost:1234/{}".format(json_name): json_content
        for json_name, json_content in load_remote_schemas()
    }
    return remote_schemas


class JsonschemaTestCase(unittest.TestCase):
    def setUp(self):
        download_suite()

    def run_test_cases(self, version):
        remote_schemas = get_remote_schemas()

        for (
            filepath,
            group_description,
            test_description,
            schema,
            instance,
            is_valid,
        ) in get_tests(version):
            test_info = textwrap.indent(
                textwrap.dedent(
                    """
                    {}
                    {}
                    {}
                    schema = {}
                    instance = {}
                    correct_answer = {}
                    """
                ).format(
                    filepath,
                    group_description,
                    test_description,
                    json.dumps(schema, indent=4),
                    json.dumps(instance, indent=4),
                    is_valid,
                ),
                " " * 4,
            )
            with self.subTest(test_info):
                s = jsonschemax.compile(schema, remote_schemas=remote_schemas)
                self.assertEqual(s(instance), is_valid)

    # def test_draft6(self):
    #     self.run_test_cases(version="draft6", validator=jsonschemax.draft6_validator)

    def test_draft7(self):
        self.run_test_cases(version="draft7")
