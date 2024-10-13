from flask import Flask, jsonify
import os
from supabase import create_client, Client
from flask import request, abort
from flask_cors import CORS
from datetime import datetime, timedelta
from schedules import schedules
from app import main

def create_app():
    app = Flask(__name__)
    CORS(app, credentials=True ,resources={r"/*": {
        "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

        # Methods
    def calculate_recurring_dates(approved_dates):
        if not approved_dates:
            return []
        # Given a list of approved dates, calculate all recurring dates for the next year
        date_list = []
        earliest_date = min([datetime.strptime(date, '%Y-%m-%d') for date in approved_dates])
        print(earliest_date)
        end_date = earliest_date + timedelta(days=365)

        # Determine the days of the week for the approved dates
        approved_weekdays = [date.weekday() for date in [datetime.strptime(date, '%Y-%m-%d') for date in approved_dates]]

        current_date = earliest_date
        while current_date <= end_date:
            if current_date.weekday() in approved_weekdays:
                date_list.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        return date_list

    def create_schedule_entries(staff_id, dates, time_slot):
        # Create schedule entries for each date in the provided list

        for date in dates:
            response = supabase.table("schedule").insert({
                "staff_id": staff_id,
                "date": date,
                "time_slot": time_slot
            }).execute()

            if response == None:
                app.logger.error("Failed to create schedule entry for date %s: %s", date, response)

    app.register_blueprint(schedules)
    app.register_blueprint(main)

    return app


