'''flaskapp'''

from flask import Flask, jsonify, request, abort, Blueprint
import os
from flask_supabase import Supabase
from flask_cors import CORS
from datetime import datetime, timedelta
from .schedules import schedule
from .main import mainapp

supabase_extension = Supabase()

def create_app():
    app = Flask(__name__)
    CORS(app, credentials=True ,resources={r"/*": {
        "origins": "http://localhost:5173", "allow_headers": ["Authorization", "Content-Type", "X-Staff-ID", "X-Role", "X-Dept"]}})  # Enable CORS for frontend origin

    app.config['SUPABASE_URL'] = "https://hyleecccrdjecquwdjmq.supabase.co"
    app.config['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5bGVlY2NjcmRqZWNxdXdkam1xIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjcxNTk0MTUsImV4cCI6MjA0MjczNTQxNX0.mkQJXXnX_ET7X72dtdzQRYeTW3psQqREdjMpCGk77H8"
    supabase_extension.init_app(app)

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

    app.register_blueprint(schedule)
    app.register_blueprint(mainapp)

    return app


