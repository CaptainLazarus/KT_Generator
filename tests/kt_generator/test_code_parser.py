import os
from kt_generator.CodeParser import CodeParser


def read_fixture_file(file_name):
    this_file_path = os.path.dirname(os.path.abspath(__file__))
    that_file_path = os.path.join(this_file_path, "fixtures", file_name)
    with open(that_file_path, "r") as f:
        return f.read()


class TestCodeParser:
    def test_extract_elements_simple_class(self):
        source_code = read_fixture_file("sample_code_001.py")
        elements = CodeParser().extract_elements(source_code, "")
        assert elements == {'Foo': {'body': 'class Foo:\n'
                                            '    def bar(self):\n'
                                            '        pass\n'
                                            '\n'
                                            '    def baz(self):\n'
                                            '        pass\n'},
                            'Foo.bar': {'body': '    def bar(self):\n        pass\n', 'class_name': 'Foo'},
                            'Foo.baz': {'body': '    def baz(self):\n        pass\n', 'class_name': 'Foo'}}
