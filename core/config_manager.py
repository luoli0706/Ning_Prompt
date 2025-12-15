import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"api_url": "", "api_key": "", "language": "en", "theme_mode": "dark"}

    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_api_url(self):
        return self.config.get("api_url", "")

    def set_api_url(self, url):
        self.config["api_url"] = url
        self._save_config()

    def get_api_key(self):
        return self.config.get("api_key", "")

    def set_api_key(self, key):
        self.config["api_key"] = key
        self._save_config()

    def get_model(self):
        return self.config.get("model", "gpt-3.5-turbo")

    def set_model(self, model):
        self.config["model"] = model
        self._save_config()

    def get_response_language(self):
        return self.config.get("response_language", "origin")

    def set_response_language(self, lang):
        self.config["response_language"] = lang
        self._save_config()

    def get_output_format(self):
        return self.config.get("output_format", "markdown")

    def set_output_format(self, fmt):
        self.config["output_format"] = fmt
        self._save_config()

    def get_language(self):
        return self.config.get("language", "en")

    def set_language(self, lang):
        self.config["language"] = lang
        self._save_config()

    def get_theme_mode(self):
        return self.config.get("theme_mode", "dark")

    def set_theme_mode(self, mode):
        self.config["theme_mode"] = mode
        self._save_config()

# Example usage (for testing)
if __name__ == "__main__":
    # Create a test config file
    test_config_file = "test_config.json"
    manager = ConfigManager(test_config_file)

    print(f"Initial API URL: {manager.get_api_url()}")
    print(f"Initial API Key: {manager.get_api_key()}")

    manager.set_api_url("https://api.example.com/v1")
    manager.set_api_key("sk-test12345")

    print(f"Updated API URL: {manager.get_api_url()}")
    print(f"Updated API Key: {manager.get_api_key()}")

    # Verify reload
    new_manager = ConfigManager(test_config_file)
    print(f"Reloaded API URL: {new_manager.get_api_url()}")
    print(f"Reloaded API Key: {new_manager.get_api_key()}")

    # Clean up test file
    if os.path.exists(test_config_file):
        os.remove(test_config_file)
