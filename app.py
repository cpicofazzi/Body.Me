import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import datetime
CAL_PER_POUND = 3_500
class FitnessTracker:
    def __init__(self):
        # Create a directory for data storage if it doesn't exist
        self.data_dir = 'fitness_data'
        # self.data_fn = "daily_data.csv"
        os.makedirs(self.data_dir, exist_ok=True)
        self.data_cols = ['Date', 'Weight', 'Calories', 'Protein']
        
        self.profiles = {
            "Christian Picofazzi": {"csv_file": "daily_data.csv"},
            "Julian Picofazzi": {"csv_file": "profile2.csv"},
            "Ava Picofazzi": {"csv_file": "profile3.csv"},
            # Add more profiles here
        }
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
            profile_data = self.profiles[selected_profile]
            data_fn = os.path.join(self.data_dir, profile_data["csv_file"])
            filename = os.path.join(self.data_dir,data_fn)
            
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
    def add_morning_entry(self, entry_date, weight, sleep_hours):
        # Ensure date is datetime
        entry_date = pd.to_datetime(entry_date)
        
        # Check if date already exists in DataFrame
        existing_entries_loc = st.session_state.entries[st.session_state.entries['Date'] == entry_date].index
        print(existing_entries_loc)
        if not existing_entries_loc.empty:
            for replace_loc in existing_entries_loc.values:
                st.session_state.entries.loc[replace_loc,"Weight"]= weight
                st.session_state.entries.loc[replace_loc,"Hours of Sleep"] = sleep_hours
        else:
            # If date does not exist, add a new row
            st.session_state.entries = pd.concat([st.session_state.entries,pd.DataFrame(
                {'Date': [entry_date],
                'Weight': [weight],
                'Calories': [0],
                'Protein': [0],
                'Hours of Sleep':[sleep_hours]},
                index=[len(st.session_state.entries)]
            )], ignore_index=True)

    def add_afternoon_entry(self, entry_date, calories, protein):
        # Ensure date is datetime
        entry_date = pd.to_datetime(entry_date)
        
        # Check if date already exists in DataFrame
        existing_entries_loc = st.session_state.entries[st.session_state.entries['Date'] == entry_date].index
        print(existing_entries_loc)
        if not existing_entries_loc.empty:
            for replace_loc in existing_entries_loc.values:
                # If date already exists, append new values to the corresponding row
                st.session_state.entries.loc[replace_loc,"Calories"]= calories
                st.session_state.entries.loc[replace_loc,"Protein"] = protein
            
            
        else:
            # If date does not exist, add a new row
            st.session_state.entries = pd.concat([st.session_state.entries,pd.DataFrame(
                {'Date': [entry_date],
                'Weight': [0],  # assuming morning weight is added separately
                'Calories': [calories],
                'Protein': [protein],
                'Hours of Sleep':[0]},
                index=[len(st.session_state.entries)]
            )], ignore_index=True)
        
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
                    value=max(st.session_state.entries['Date'])
                )
            
                if st.form_submit_button("Delete Entry"):
                    self.remove_entry_by_date(selected_date)
                    
                self.save_to_csv()
        
        
    def add_entry_morning_form(self):
        col1, col2, col3 = st.columns(3, vertical_alignment="center",border=False)
        
        with col1:
            entry_date = st.date_input("Date", key="morning_date")
            weight = st.number_input("Weight (lbs)", min_value=150.0, step=0.1, key="weight_input")
        with col2:
            sleep_hours = st.selectbox("Hours of Sleep", options=["<5","5-6","6-7","7-8","8-9","9-10",">10"], key="sleep_hours_input")
            sleep_quality = st.slider("Sleep Quality", min_value=0,max_value=10,step=1, key="sleep_quality")
            
        with col3:
            bed_phone = st.checkbox("Phone before bed?", value=False,key="bed_phone")
            drink_or_smoke = st.checkbox("Drink or Smoke?", value=False, key="drink_or_smoke")
            night_terror = st.checkbox("Night Terror", value=False,key="night_terror")
       
        dreams_text = st.text_area("Describe Dreams")    
        # Create a form
        morning_form = st.form("Morning_Entry_Form")
        
        # Add the submit button within the form
        with morning_form:
            submit_button = st.form_submit_button("Add Morning Entry")
            
        if submit_button:
            self.add_morning_entry(entry_date, weight,sleep_hours)

    def add_entry_night_form(self):
        col1, col2, col3= st.columns(3,vertical_alignment='top')
        
        with col1:
            entry_date = st.date_input("Date", key="night_date")
            calories = st.number_input("Calories", min_value=0, key="calories_input")
            dumps = st.number_input("#2", min_value=0, key="dumps")
        with col2:
            
            protein = st.number_input("Protein", min_value=0, key="protein_input")
            carbs = st.number_input("Carbs", min_value=0, key="carbs_input")
            fats = st.number_input("Fats", min_value=0, key="fats_input")
        with col3:
            day_quality = st.slider("Day Quality", min_value=0,max_value=10,step=1, key="day_quality")
            work_quality = st.slider("Work Quality", min_value=0,max_value=10,step=1, key="work_quality")
            
        accomplishments = st.multiselect("Daily Activities and Things", options=[
            "Workout","Cardio","Soccer","Mobility","Spanish","Japanese","Coding Project",
            "Books","Reading Research","Sick","Sunshine","Creatine","Vitamins","Smoke","Drink","Date",";)","Video Games"])
        
        what_happened_text = st.text_area("What happened today?")
        # Create a form
        night_form = st.form("Night_Entry_Form")
        
        # Add the submit button within the form
        with night_form:
            submit_button = st.form_submit_button("Add Night Entry")

        if submit_button:
            self.add_afternoon_entry(entry_date, calories, protein)
    
    def create_calorie_fill_up_widget(self):
        """
        Create widget showing filling up of allocated calories per week
        """
        # Calculate weekly calorie allocation and current week's fill-up percentage
        st.session_state.entries['Week'] = pd.to_datetime(st.session_state.entries['Date']).dt.isocalendar().week
        st.session_state.entries['Year'] = pd.to_datetime(st.session_state.entries['Date']).dt.isocalendar().year
        st.session_state.entries['Year_Week'] = st.session_state.entries['Year'].astype(str) + '_' + st.session_state.entries['Week'].astype(str).str.zfill(2)
        weekly_allocation = 17_500  # Assuming a standard weekly allocation of 17_500 calories
        today = datetime.datetime.today()
        current_yearweek = f"{today.isocalendar().year}_{str(today.isocalendar().week).zfill(2)}"
        
        current_week_fill_up = (st.session_state.entries[st.session_state.entries['Year_Week'] == current_yearweek]['Calories'].sum()) / weekly_allocation 
       
        
        col1, col2 = st.columns(2)
        
        with col1:
            fill_up_bar = st.progress(current_week_fill_up)

        with col2:
            current_week_calories = st.session_state.entries[st.session_state.entries['Year_Week'] == current_yearweek]['Calories'].sum()
            display_text = f"Current Week: {current_week_calories} / {weekly_allocation}"
            st.write(display_text)
        
        # Historical fill up barchart
        st.plotly_chart(self._make_bar_plot(column_name="Calories"))
 
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

    def _make_bar_plot(self, column_name: str) -> go.Figure():
        # Ensure Date column is datetime
        st.session_state.entries['Date'] = pd.to_datetime(st.session_state.entries['Date'])
        
        # Group by Year-Week and calculate sum of calories for each group
        grouped_entries = st.session_state.entries.groupby('Year_Week')[column_name].sum().reset_index()
        
        fig = go.Figure()
        # Bar Chart
        max_calories = st.session_state.entries.groupby('Year_Week')['Calories'].max().reset_index()
        min_calories = st.session_state.entries.groupby('Year_Week')['Calories'].min().reset_index()
        # Sort entries by date
        sorted_grouped_entries = grouped_entries.sort_values('Year_Week')
        
        goal_threshold = 17_500
        main_threshold = 21_000
        
        bar_colors = []
        for y_value in sorted_grouped_entries[column_name]:
            if y_value > main_threshold:
                bar_colors.append("rgba(255, 22, 0, 0.68)") # Red color
            elif y_value > goal_threshold:
                bar_colors.append("rgba(255, 207, 56, 0.51)") # orange color
            else:
                bar_colors.append("rgba(99, 219, 67, 0.51)") # green color
        
        years = [int(year) for year in sorted_grouped_entries['Year_Week'].str.split('_').str[0]]
        weeks = [int(week) % 52 + 1 for week in sorted_grouped_entries['Year_Week'].str.split('_').str[1]]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        month_names = [f"{month} {year}" for year, week, month in zip(years, weeks, months)]
        
        fig.add_trace(go.Bar(
            x=month_names,
            y=sorted_grouped_entries[column_name],
            name="Weekly Calories",
            marker=dict(color=bar_colors) 
        ))
        threshold_line = go.Scatter(
            x=month_names,
            y=[main_threshold] * len(month_names),
            mode='lines',
            line=dict(color="red", width=2, dash="dash"),
            name=f"Maintenence Threshold \n({main_threshold} calories)"
        )
        goal_line = go.Scatter(
            x=month_names,
            y=[goal_threshold] * len(month_names),
            mode='lines',
            line=dict(color="green", width=1, dash="dashdot"),
            name=f"Goal Threshold \n({goal_threshold} calories)"
        )
        
        fig.add_trace(threshold_line)
        fig.add_trace(goal_line)
        
        # Add hover-over text for each bar
        # for i, trace in enumerate(fig.data):
        fig.add_trace(go.Scatter(
            x=month_names,
            y=[0] * len(month_names),
            mode='lines',
            line=dict(color="black", width=0.5),
            hoverinfo='text',
            hovertext=[f"{yearmonth} |    {(goal_threshold - y_value)/CAL_PER_POUND:.2f} to goal  {(main_threshold - y_value)/CAL_PER_POUND:.2f} to maintain" for yearmonth, y_value, in zip(month_names, sorted_grouped_entries[column_name],)],
            showlegend=False,
        ),
                    )

        fig.update_layout(
            hovermode='x',
            xaxis_title='Month and Year',
            yaxis_title='Weekly Calories',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.01,
                xanchor="right",
                x=1
            ),
            hoverlabel=dict(
                bgcolor="#f7d2c4",  # Add this line, change the color as needed
                bordercolor="#666",
                font_size=18,
            )
        )
        
        return fig

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
        fig.update_layout(
            hovermode='x',
            xaxis_title='Date',
            yaxis_title=column_name,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.01,
                xanchor="right",
                x=1
            ),
            hoverlabel=dict(
                bgcolor="#f7d2c4",  # Add this line, change the color as needed
                bordercolor="#666",
                font_size=18,
            )
        )
        return fig
    
    def load_data(self, selected_profile):
        """
        Load data from the selected profile's csv file.
        """
        profile_data = self.profiles[selected_profile]
        data_fn_path = os.path.join(self.data_dir, profile_data["csv_file"])
        
        if not os.path.exists(data_fn_path):
            st.error(f"No CSV file found for {selected_profile}")
            return
        
        try:
            self.load_csv(data_fn_path)
            
        except Exception as e:
            st.error(f"Failed to load data: {e}")

    def app(self):
        """
        Main Streamlit application
        """
        st.title("Body.Me")
        profile_names = list(self.profiles.keys())
        selected_profile = st.selectbox('Select Profile', options=profile_names)
        # Sidebar for CSV operations
        with st.sidebar:
            
            st.header("CSV Operations")
            
            # CSV Upload
            uploaded_file = st.file_uploader("Load Previous Entries", type=['csv'])
            
            if uploaded_file is not None:
                self.load_csv(uploaded_file)  
            # Save Current Entries Button
            if st.button("Save Current Entries"):
                self.save_to_csv()
                
                
        
        
        # Load data from the selected profile
        self.load_data(selected_profile)
        
        tab1, tab2 = st.tabs(["Morning Form", "Night Form"])
                
        with tab1:
            self.add_entry_morning_form()

        with tab2:
            self.add_entry_night_form()
        
        self.create_calorie_fill_up_widget()
        # Display entries and visualizations
        with st.expander("Entries"):
            self.display_entries()
            self.delete_button()
        self.create_visualizations()

# Run the app
if __name__ == "__main__":
    tracker = FitnessTracker()
    tracker.app()