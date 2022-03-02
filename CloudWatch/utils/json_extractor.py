import json

class JsonExtractor:
    @classmethod
    def from_file(self, file_path):
        file = open(file_path)
        content_json = json.loads(file.read())
        file.close()
        return content_json