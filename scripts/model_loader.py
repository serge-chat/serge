import configparser
import os
from typing import List


class ModelLoader:
    def __init__(self):
        self.model_extensions = self._load_model_extensions()

    def _load_model_extensions(self) -> List[str]:
        config = configparser.ConfigParser()
        config.read('config.ini')
        extensions = config.get('ModelConfig', 'modelFileExtensions').split(',')
        return extensions

    def validate_model_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            return False
        if not os.path.isfile(file_path):
            return False
        _, ext = os.path.splitext(file_path)
        if ext not in self.model_extensions:
            return False
        return True

    def load_model(self, file_path: str):
        if not self.validate_model_file(file_path):
            raise ValueError(f"Model file {file_path} is not valid or supported.")
        # Assuming the application uses a generic load function for models
        # This part would be replaced with the actual model loading logic
        print(f"Loading model from {file_path}")
        # Load the model here

# Unit tests covering all edge cases
import unittest
from unittest.mock import patch


class TestModelLoader(unittest.TestCase):
    def setUp(self):
        self.loader = ModelLoader()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    def test_validate_model_file_valid(self, mock_isfile, mock_exists):
        self.assertTrue(self.loader.validate_model_file("model.bin"))

    @patch('os.path.exists', return_value=False)
    def test_validate_model_file_nonexistent(self, mock_exists):
        self.assertFalse(self.loader.validate_model_file("nonexistent.bin"))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=False)
    def test_validate_model_file_not_a_file(self, mock_isfile, mock_exists):
        self.assertFalse(self.loader.validate_model_file("directory"))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    def test_validate_model_file_unsupported_extension(self, mock_isfile, mock_exists):
        self.assertFalse(self.loader.validate_model_file("unsupported.txt"))

    @patch.object(ModelLoader, 'validate_model_file', return_value=True)
    def test_load_model_valid(self, mock_validate):
        with patch('builtins.print') as mock_print:
            self.loader.load_model("model.bin")
            mock_print.assert_called_with("Loading model from model.bin")

    @patch.object(ModelLoader, 'validate_model_file', return_value=False)
    def test_load_model_invalid(self, mock_validate):
        with self.assertRaises(ValueError):
            self.loader.load_model("invalid.txt")

if __name__ == '__main__':
    unittest.main()
