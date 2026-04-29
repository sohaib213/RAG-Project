import importlib


class TemplateParser:

    def __init__(self, language: str = "en"):
        self.language = language

    def set_language(self, language: str):
        self.language = language

    def get(self, template_name: str, key: str, variables: dict = {}):
        # Dynamically load the right language file
        module_path = f"stores.llm.tempelate.locales.{self.language}.{template_name}"
        module = importlib.import_module(module_path)

        # Get the template string by key name
        template = getattr(module, key)

        # Fill in any variables like {doc_num} or {text}
        for var_key, var_value in variables.items():
            template = template.replace("{" + var_key + "}", str(var_value))

        return template