import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

class FitnessTracker:
    def __init__(self):
        # Create a directory for data storage if it doesn't exist
        self.data_dir = 'fitness_data'
        self.data_fn = "daily_data.csv"
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_cols = ['Date', 'Weight', 'Calories', 'Protein']
        # Initialize session state for storing entries
        if 'entries' not in st.session_state:
            st.session_state.entries = pd.DataFrame(columns=self.data_cols)

    def save_to_csv(self):
        """
        Save current entries to a CSV file with a timestamp in the filename
        """
        try:
            # Ensure Date is in string format for consistent saving
            save_df = st.session_state.entries.copy()
            save_df['Date'] = save_df['Date'].astype(str)
            
            # Generate filename with current timestamp
            filename = os.path.join(self.data_dir,self.data_fn)
            
            save_df.to_csv(filename, index=False)
            st.success(f"Entries saved to {filename}")
        except Exception as e:
            st.error(f"Error saving CSV: {e}")

    def load_csv(self, uploaded_file):
        """
        Load entries from an uploaded CSV file
        """
        try:
            # Read the uploaded CSV file
            loaded_df = pd.read_csv(uploaded_file)
            
            # Validate the DataFrame has required columns
            required_columns = self.data_cols
            if not all(col in loaded_df.columns for col in required_columns):
                st.error("Invalid CSV format. Required columns: Date, Weight, Calories")
                return
            
            # Convert Date column to datetime
            loaded_df['Date'] = pd.to_datetime(loaded_df['Date'])
            
            # Update session state with loaded entries
            st.session_state.entries = loaded_df
            st.success("Entries loaded successfully!")
        
        except Exception as e:
            st.error(f"Error loading CSV: {e}")

    def add_entry(self, date, weight, calories, protein):
        """
        Add a new entry to the fitness tracker with robust error checking
        """
        try:
            # Validate inputs
            if not date:
                st.error("Date cannot be empty")
                return False
            
            if weight <= 0:
                st.error("Weight must be a positive number")
                return False
            
            if calories < 0:
                st.error("Calories cannot be negative")
                return False
            
            if protein < 0:
                st.error("Protein cannot be negative")
                return False
            
            # Create a new entry
            new_entry = pd.DataFrame({
                'Date': [pd.to_datetime(date)],
                'Weight': [float(weight)],  # Ensure float conversion
                'Calories': [int(calories)],  # Ensure integer conversion
                'Protein':[int(protein)]
            })
            
            # Append to existing entries
            st.session_state.entries = pd.concat([
                st.session_state.entries, 
                new_entry
            ]).reset_index(drop=True)
            
            return True
        
        except Exception as e:
            st.error(f"Error adding entry: {e}")
            return False

    def remove_entry_by_date(self, date_rem):
        """
        Remove an entry by index with error handling
        """
        try:
            matching_indices = st.session_state.entries[st.session_state.entries['Date'] == pd.to_datetime(date_rem)].index
            print(f"Matching {matching_indices}\n{st.session_state.entries['Date']} to {date_rem}")
            for index in sorted(matching_indices, reverse=True):
                st.session_state.entries = st.session_state.entries.drop(index).reset_index(drop=True)
        except Exception as e:
            st.error(f"Error removing entry: {e}")

    def delete_button(self):
        # Add delete button
        if len(st.session_state.entries)>0:
            with st.form("delete_entry", clear_on_submit=True):
                selected_date = st.date_input(
                    "Select Date to Delete",
                    value=min(st.session_state.entries['Date'])
                )
            
                if st.form_submit_button("Delete Entry"):
                    self.remove_entry_by_date(selected_date)
                    
        self.save_to_csv()
        
    def input_form(self):
        """
        Generate input form.
        """
        # Input form
        with st.form("fitness_entry", clear_on_submit=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                entry_date = st.date_input("Date")
            
            with col2:
                weight = st.number_input("Weight (lbs)", min_value=0.0, step=0.1, key="weight_input")
            
            with col3:
                calories = st.number_input("Calories", min_value=0, key="calories_input")
            with col4:
                protein = st.number_input("Protein", min_value=0, key="protein_input")
            
            submit_button = st.form_submit_button("Add Entry")
            
            if submit_button:
                success = self.add_entry(entry_date, weight, calories,protein)
                if success:
                    st.success("Entry added successfully!")            
                    
            
            
    def display_entries(self):
        """
        Display existing entries and provide delete functionality
        """
        st.subheader("Existing Entries")
        
        if len(st.session_state.entries) > 0:
            # Display the table with index reset
            entries_display = st.session_state.entries.reset_index(drop=True).sort_values('Date',ascending=False)
            
            st.dataframe(entries_display)

    def create_visualizations(self):
        """
        Create data visualizations for weight and calories
        """
        if len(st.session_state.entries) > 0:
            
            
            # Create two tabs for different visualizations
            tab1, tab2, tab3 = st.tabs(["Weight Trend", "Calories Trend","Protein Trend"])

            with tab1:
                st.plotly_chart(self._make_line_plot(column_name="Weight"))
            
            with tab2:
                st.plotly_chart(self._make_line_plot(column_name="Calories"))
            with tab3:
                st.plotly_chart(self._make_line_plot(column_name="Protein"))

    def _make_line_plot(self, column_name: str) -> go.Figure():
        
        # Ensure Date column is datetime
        st.session_state.entries['Date'] = pd.to_datetime(st.session_state.entries['Date'])
        
        # Sort entries by date
        sorted_entries = st.session_state.entries.sort_values('Date')
        fig = go.Figure()
        # Line Chart
        fig_calories = fig.add_trace(go.Scatter(
                x=sorted_entries['Date'],
                y=sorted_entries[column_name],
                mode='lines',
                name=column_name,
                line=dict(color='rgba(14, 149, 255, 0.33)', width=0.5)
        ))
        
        # Add rolling average to the line chart
        rolling_avg = sorted_entries[column_name].rolling(window=30).mean()
        fig.add_scatter(
            x=sorted_entries['Date'],
            y=rolling_avg,
            name='Monthly Rolling Average',
            line=dict(color='rgba(94, 135, 172, 1)', width=1.0)
        )
        
        # Add rolling average to the line chart
        rolling_avg = sorted_entries[column_name].rolling(window=90).mean()
        fig.add_scatter(
            x=sorted_entries['Date'],
            y=rolling_avg,
            name='Quarterly Rolling Average',
            line=dict(color='rgba(0, 173, 114, 1)', width=1.0)
        )
        return fig

    def app(self):
        """
        Main Streamlit application
        """
        st.title("Body.Me")
        
        # Sidebar for CSV operations
        with st.sidebar:
            if st.button('Show/Hide CSV Operations'):
                st.header("CSV Operations")
                
                # CSV Upload
                uploaded_file = st.file_uploader("Load Previous Entries", type=['csv'])
                print(uploaded_file, type(uploaded_file))
                if uploaded_file is not None:
                    self.load_csv(uploaded_file)  
                # Save Current Entries Button
                if st.button("Save Current Entries"):
                    self.save_to_csv()
            else:
                self.load_csv(os.path.join(self.data_dir,self.data_fn))
        
        self.input_form()
        
        # Display entries and visualizations
        self.display_entries()
        self.delete_button()
        self.create_visualizations()

# Run the app
if __name__ == "__main__":
    tracker = FitnessTracker()
    tracker.app()