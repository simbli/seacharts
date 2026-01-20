from datetime import datetime, timedelta

class Time:
    """
    Time class that generates a sequence of datetime objects and their corresponding 
    epoch times based on a specified start and end time, a time period (e.g., hour, day), 
    and a period multiplier.

    :param time_start: String representing the start datetime in "DD-MM-YYYY HH:MM" format.
    :param time_end: String representing the end datetime in "DD-MM-YYYY HH:MM" format.
    :param period: String representing the time increment (e.g., 'hour', 'day', 'month').
    :param period_mult: Multiplier for the period to extend or reduce intervals.
    """
    def __init__(self, time_start: str, time_end: str, period: str, period_mult: float):
            # Store the multiplier for the period
            self.period_mult = period_mult

            # Define the format for parsing date strings
            self._date_string_format = "%d-%m-%Y %H:%M"

            # Parse start and end times using the defined format
            self.time_start = datetime.strptime(time_start, self._date_string_format)
            self.time_end = datetime.strptime(time_end, self._date_string_format)

            # Store the period type (e.g., 'hour', 'day', etc.)
            self.period = period
            
            # Generate the list of datetimes and epoch times
            self.datetimes = self._generate_datetimes()
            self.epoch_times = [int(dt.timestamp()) for dt in self.datetimes]
        
    def _generate_datetimes(self) -> list[datetime]:
        """
        Generates a list of datetime objects within the time range from 'time_start'
        to 'time_end' based on the specified period and multiplier.
        
        :return: List of datetime objects from start to end.
        """
        current_time = self.time_start
        datetimes: list[datetime] = []

        # Generate datetimes by incrementing until reaching the end time
        while current_time <= self.time_end:
            datetimes.append(current_time)
            current_time = self._increment_time(current_time)
        
        return datetimes

    def _increment_time(self, current_time: datetime) -> datetime:
        """
        Increment the given datetime by the specified period and multiplier.
        
        :param current_time: The datetime to increment.
        :return: A new datetime object incremented by the specified period.
        """
        if self.period == "hour":
            return current_time + timedelta(hours=int(1 * self.period_mult))
        elif self.period == "day":
            return current_time + timedelta(days=int(1 * self.period_mult))
        elif self.period == "week":
            return current_time + timedelta(weeks=int(1 * self.period_mult))
        elif self.period == "month":
            new_month = current_time.month + 1 if current_time.month < 12 else 1
            new_year = current_time.year if current_time.month < 12 else current_time.year + 1
            return current_time.replace(year=new_year, month=new_month, day=1)
        elif self.period == "year":
            return current_time.replace(year=current_time.year + 1, month=1, day=1)
        else:
            raise ValueError(f"Unknown period: {self.period}")
        
    def get_datetimes_strings(self) -> list[str]:
        """
        Returns a list of formatted datetime strings for all generated datetime objects.
        
        :return: List of datetime strings in "DD-MM-YYYY HH:MM" format.
        """
        return [datetime.strftime(self._date_string_format) for datetime in self.datetimes]