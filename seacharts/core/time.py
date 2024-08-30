from datetime import datetime, timedelta

class Time:
    def __init__(self, time_start: str, time_end: str, period: str):
            # Parse the start and end dates
            self._date_string_format = "%d-%m-%Y %H:%M"
            self.time_start = datetime.strptime(time_start, self._date_string_format)
            self.time_end = datetime.strptime(time_end, self._date_string_format)
            self.period = period
            
            # Generate the list of datetimes and epoch times
            self.datetimes = self._generate_datetimes()
            self.epoch_times = [int(dt.timestamp()) for dt in self.datetimes]
        
    def _generate_datetimes(self):
        """Generate a list of datetime objects based on the period."""
        current_time = self.time_start
        datetimes = []

        while current_time <= self.time_end:
            datetimes.append(current_time)
            current_time = self._increment_time(current_time)
        
        return datetimes

    def _increment_time(self, current_time):
        """Increment the datetime based on the specified period."""
        if self.period == "hour":
            return current_time + timedelta(hours=1)
        elif self.period == "day":
            return current_time + timedelta(days=1)
        elif self.period == "week":
            return current_time + timedelta(weeks=1)
        elif self.period == "month":
            new_month = current_time.month + 1 if current_time.month < 12 else 1
            new_year = current_time.year if current_time.month < 12 else current_time.year + 1
            return current_time.replace(year=new_year, month=new_month, day=1)
        elif self.period == "year":
            return current_time.replace(year=current_time.year + 1, month=1, day=1)
        else:
            raise ValueError(f"Unknown period: {self.period}")
        
    def get_datetimes_strings(self):
        return [datetime.strftime(self._date_string_format) for datetime in self.datetimes]