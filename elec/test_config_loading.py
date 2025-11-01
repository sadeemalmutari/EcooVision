import unittest
from modules.data_handler import CSVDataHandler

class TestCSVDataHandler(unittest.TestCase):
    def test_load_csv_success(self):
        handler = CSVDataHandler()
        # Create a sample DataFrame and save as CSV for testing
        df = pd.DataFrame({'base_kw': [7.5] * 30})
        test_csv = 'test_config.yaml'
        df.to_csv(test_csv, index=False)
        
        try:
            handler.load_csv(test_csv, 30)
            self.assertIsNotNone(handler.data)
            self.assertEqual(len(handler.data), 30)
        finally:
            import os
            os.remove(test_csv)
    
    def test_load_csv_missing_column(self):
        handler = CSVDataHandler()
        df = pd.DataFrame({'wrong_column': [7.5] * 30})
        test_csv = 'test_config_missing.yaml'
        df.to_csv(test_csv, index=False)
        
        with self.assertRaises(ValueError):
            handler.load_csv(test_csv, 30)
        
        import os
        os.remove(test_csv)
    
    def test_load_csv_incorrect_rows(self):
        handler = CSVDataHandler()
        df = pd.DataFrame({'base_kw': [7.5] * 25})  # 25 rows instead of 30
        test_csv = 'test_config_incorrect_rows.yaml'
        df.to_csv(test_csv, index=False)
        
        with self.assertRaises(ValueError):
            handler.load_csv(test_csv, 30)
        
        import os
        os.remove(test_csv)

if __name__ == '__main__':
    unittest.main()
