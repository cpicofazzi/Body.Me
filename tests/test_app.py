import unittest
from app import FitnessTracker
import tempfile
import os
import pandas as pd

class TestFitnessTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = FitnessTracker()

    def test_add_entry_morning_form(self):
        with tempfile.NamedTemporaryFile(suffix='.csv') as tmp:
            tmp_path = tmp.name
            self.tracker.add_entry_morning_form(tmp_path)
            entries = pd.read_csv(tmp_path)
            self.assertEqual(len(entries), 1)

    def test_load_data(self):
        profile_name = 'test_profile'
        self.tracker.profiles[profile_name] = {'csv_file': 'test.csv'}

        # Create a test-specific temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = os.path.join(tmp_dir, 'test.csv')
            pd.DataFrame({'column1': [1, 2, 3]}).to_csv(csv_path, index=False)
            self.tracker.load_data(profile_name)
            entries = self.tracker.st.session_state.entries
            self.assertEqual(len(entries), 3)

    def test_create_calorie_fill_up_widget(self):
        # Create a sample dataframe with entries
        entries = pd.DataFrame({'Date': ['2022-01-01', '2022-01-02'], 'Calories': [1000, 2000]})
        self.tracker.entries = entries
        self.tracker.create_calorie_fill_up_widget()
        # Assert that the widget is rendered correctly

    def test_display_entries(self):
        # Create a sample dataframe with entries
        entries = pd.DataFrame({'Date': ['2022-01-01', '2022-01-02'], 'Calories': [1000, 2000]})
        self.tracker.entries = entries
        self.tracker.display_entries()
        # Assert that the table is rendered correctly

    def test_create_visualizations(self):
        # Create a sample dataframe with entries
        entries = pd.DataFrame({'Date': ['2022-01-01', '2022-01-02'], 'Calories': [1000, 2000]})
        self.tracker.entries = entries
        self.tracker.create_visualizations()
        # Assert that the visualizations are rendered correctly

    def test_delete_button(self):
        # Create a sample dataframe with entries
        entries = pd.DataFrame({'Date': ['2022-01-01', '2022-01-02'], 'Calories': [1000, 2000]})
        self.tracker.entries = entries
        self.tracker.display_entries()
        delete_button = self.tracker.delete_button()
        # Assert that the button is rendered correctly

if __name__ == '__main__':
    unittest.main()