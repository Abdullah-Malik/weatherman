"""
Weatherman Task
"""

import argparse
import os
from termcolor import colored

parser = argparse.ArgumentParser()
parser.add_argument("-a", nargs="?", default="", type=str)
parser.add_argument("-e", nargs="?", default="", type=str)
parser.add_argument("-c", nargs="?", default="", type=str)
args = parser.parse_args()

NUM_TO_MONTH = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)
NUM_TO_FULL_MONTH_NAME = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


class FileReader:
    """
        A class for parsing the files and populating the readings data structure
    """
    @staticmethod
    def get_single_file_path(date_str):
        """
        Takes the date in yyyy/mm format as input and
        returns the weather file path for the given input year and month

        Parameters:
            date_str: string in yyyy/mm format

        Returns:
            list containing a string that is the path to
            the file for the particular month and year value
        """

        year, month = date_str.split("/")
        path = (
            "weatherfiles/Murree_weather_"
            + str(year)
            + "_"
            + NUM_TO_MONTH[int(month) - 1]
            + ".txt"
        )

        if os.path.isfile(path):
            return path
        return f"File for {date_str} does not exist"

    @staticmethod
    def get_filepaths(year):
        """
        Takes the date in yyyy format and returns a list that contains
         the path to all the weather data files for the particular given year

        Parameters:
            year: string in yyyy

        Returns:
            Returns a list that contains the path to all
             the weather data files for the particular given year
        """

        dir_path = "weatherfiles/"
        year_filename = "Murree_weather_" + str(year)
        file_names = []

        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)

            if os.path.isfile(file_path) and filename.startswith(year_filename):
                file_names.append(os.path.join(dir_path, filename))

        return file_names

    @staticmethod
    def convert_to_numeric(val):
        """
        Takes a string as input and convert it to either int or float. If a given string
        can't be converted to int or float then the same string is returned

        Parameters:
            val: string

        Returns:
           returns either int or float depending on the input string.
        """

        try:
            return int(val)
        except ValueError:
            pass

        try:
            return float(val)
        except ValueError:
            return None

    def read_files(self, filenames):
        """
        Reads the paths of the files from the input filename_list and returns the contents of
        the file

        Parameters:
            filename_list: list containing path to weather data files

        Returns:
            readings: List of string with each string carrying data of a unique row in the
            weather data files

        """
        readings = []
        row_data = []

        for filename in filenames:
            with open(filename, "r") as my_file:
                file_lines = my_file.readlines()

            for line in file_lines[1:]:
                row_data = []

                for val in line.split(","):
                    num_value = self.convert_to_numeric(val)

                    if num_value is not None:
                        row_data.append(num_value)
                    else:
                        row_data.append(val)

                readings.append(row_data)

        return readings

    def process_files(self):
        """
        Read files depending upon the different flag and return weather_readings dictionary

        Returns:
            weather_readings: A dictionary that can have keys including e, c and a and the
             values are list of strings that carry data of relevant files
        """

        weather_readings = {}

        if args.c:
            filepath = self.get_single_file_path(args.c)
            filepath = [filepath]
            weather_readings["c"] = self.read_files(filepath)

        if args.a:
            filepath = self.get_single_file_path(args.a)
            filepath = [filepath]
            weather_readings["a"] = self.read_files(filepath)

        if args.e:
            weather_readings["e"] = self.read_files(self.get_filepaths(args.e))

        return weather_readings


class ResultCalculator:
    """
        A class for computing the calculations given the readings data structure
    """
    @staticmethod
    def check_values(str1, str2):
        """
        Checks if both the input arguments are non-empty strings

        Parameters:
            str: string
            str: string

        Returns:
            returns True if both the input arguments are non-empty strings else returns false
        """

        return bool(str1 and str2)

    def find_min_max_temperature_for_each_day(self, readings):
        """
        Find the min and max temperature for all days in the given data

        Parameters:
            readings: List of strings carrying the data of the relevant files. Each string
             element carries data from exactly one row of a relevant file

        Returns:
            list of (max, min) tuples containing max and min temperature for all the
            days in a month
        """

        max_min_temp = []

        for line in readings:
            if self.check_values(line[1], line[3]):
                max_min_temp.append((line[1], line[3]))

        return {"daily_temperatures": max_min_temp}

    @staticmethod
    def find_avg_of_min_max_temperatures_and_humidity(readings):
        """
        Compute average max temperature, average min temperature, and average humidity
        values from the given data

        Parameters:
            readings: List of strings carrying the data of the relevant files. Each
            string element carries data from exactly one row of a relevant file

        Returns:
            Returns a dictionary containing average max temperature, average min
            temperature, and average humidity values computed for a given month
        """

        average_mean_humidity = 0
        average_max_temp = 0
        average_min_temp = 0

        for line in readings:
            if line[1]:
                average_max_temp += line[1]

            if line[3]:
                average_min_temp += line[3]

            if line[8]:
                average_mean_humidity += line[8]

        average_mean_humidity = average_mean_humidity / len(readings)
        average_max_temp = average_max_temp / len(readings)
        average_min_temp = average_min_temp / len(readings)

        return {
            "avg_max_temp": average_max_temp,
            "avg_min_temp": average_min_temp,
            "mean_humidity": average_mean_humidity,
        }

    @staticmethod
    def find_min_max_temperature_and_humidity_in_a_year(readings):
        """
        Find the highest temperature, Lowest temprature and highest humidity etc
         during a period of 1 year

        Parameters:
            readings: List of strings carrying the data of the relevant files.
            Each string element carries data from exactly one row of a relevant file

        Returns:
            Returns a dictionary containing the highest temperature,
            Lowest temprature and highest humidity values etc during a period of 1 year
        """

        max_temperature = -1000
        max_temperature_day = ""
        min_temperature = 1000
        min_temperature_day = ""
        max_humidity = -1000
        max_humidity_day = ""

        for line in readings:
            day = line[0]
            max_temp = line[1]
            min_temp = line[3]
            max_humid = line[7]

            if max_temp and max_temperature < max_temp:
                max_temperature = max_temp
                max_temperature_day = day

            if min_temp and min_temperature > min_temp:
                min_temperature = min_temp
                min_temperature_day = day

            if max_humid and max_humidity < max_humid:
                max_humidity = max_humid
                max_humidity_day = day

        return {
            "max_temp": max_temperature,
            "max_day": max_temperature_day,
            "min_temp": min_temperature,
            "min_day": min_temperature_day,
            "max_humidity": max_humidity,
            "humid_day": max_humidity_day,
        }

    def process_readings(self, readings, flag):
        """
        Takes readings as input and performs calculations on the data

        Parameters:
            flag: A string that can have 'a', 'c' and 'e' as value
            readings: List of strings carrying the data of the relevant files.
            Each string element carries data from exactly one row of a relevant file

        Returns:
            returns the calculated results from the data

        """

        ret_val = "No flag matched"
        if flag == "c":
            ret_val = self.find_min_max_temperature_for_each_day(readings)
        elif flag == "a":
            ret_val = self.find_avg_of_min_max_temperatures_and_humidity(readings)
        elif flag == "e":
            ret_val = self.find_min_max_temperature_and_humidity_in_a_year(readings)

        return ret_val

    def compute_results(self, weather_readings):
        """
        Takes the weather readings dictionary as input and perform calculations
        on it

        Parameters:
            weather_readings: A dictionary that can have keys including e, c and a
            and the values are list of strings that carry data of relevant files

        Returns:
            result_dict: A dictionary that can have keys including e, c and a, and
            the values will be dictionary containing the computed results.
        """

        result_dict = {}

        for flag, file_contents in weather_readings.items():
            result_dict[flag] = self.process_readings(file_contents, flag)

        return result_dict


class ResultProcessor:
    """
        A class for creating the reports given the results data structure
    """
    @staticmethod
    def check_values(str1, str2):
        """
        Checks if both the input arguments are non-empty strings

        Parameters:
            str1: string
            str2: string

        Returns:
            returns True if both the input arguments are non-empty strings else
            returns false
        """

        return bool(str1 and str2)

    @staticmethod
    def get_full_month_name_from_date(date_string):
        """
        Converts yyyy-mm-dd string as input and return first three letters of
        the name of the month along with the day

        Parameters:
            date_string: str with the following date format yyyy-mm-dd

        Returns:
            string that has the first three letters of month combined with the day
        """

        _, month, day = date_string.split("-")
        month = int(month)

        return NUM_TO_FULL_MONTH_NAME[month - 1] + " " + str(day)

    def print_temperature_range_using_min_max_temperatures(self, results):
        """
        Functions produces report by using data from the results dictionary

        Parameters:
            results: A dictionary list of min and max temperatures for all the
            days in a particular month
        """

        print("Report for c")

        for i, tup in enumerate(results["daily_temperatures"]):
            my_max, my_min = tup

            if self.check_values(my_max, my_min):
                blues = "+" * my_min
                reds = "+" * (my_max - my_min)
                print(
                    f'{i+1} { colored(blues, "blue")}{colored(reds, "red")} {my_min}C - {my_max}C'
                )
        print()

    @staticmethod
    def print_avg_of_min_max_temperatures_and_humidity(results):
        """
        Functions produces report by printing calculations from the
        results dictionary

        Parameters:
            results: A dictionary containing average max temperature,
            average min temperature etc for a particular month
        """

        print("Report for a")
        print(f'Highest Average: {results["avg_max_temp"]:.1f}C')
        print(f'Lowest Average: {results["avg_min_temp"]:.1f}C')
        print(f'Average Mean Humidity: {results["mean_humidity"]:.2f}%')
        print()

    def print_min_max_temperature_and_humidity_in_a_year(self, results):
        """
        Functions produces report by printing calculations from the results dictionary

        Parameters:
            results: A dictionary containing max temperature, min temperature etc
            for a particular year
        """

        print("Report for e")

        max_day = self.get_full_month_name_from_date(results["max_day"])
        print(f'Highest: {results["max_temp"]}C on {max_day}')

        min_day = self.get_full_month_name_from_date(results["min_day"])
        print(f'Lowest: {results["min_temp"]}C on {min_day}')

        max_humidity = self.get_full_month_name_from_date(results["humid_day"])
        print(f'Humidity: {results["max_humidity"]}% on {max_humidity}')

    def produce_report(self, weather_result):
        """
        The functions takes the computed results and generate report

        Parameters:
            weather_results: A dictionary containing different key, value pairs.
            The keys include e, a, and c. The values are dictionaries
            containing different key,value pairs.

        """

        for flag, results in weather_result.items():

            if flag == "c":
                self.print_temperature_range_using_min_max_temperatures(results)

            elif flag == "a":
                self.print_avg_of_min_max_temperatures_and_humidity(results)

            elif flag == "e":
                self.print_min_max_temperature_and_humidity_in_a_year(results)


if __name__ == "__main__":
    fr = FileReader()
    _readings = fr.process_files()
    rc = ResultCalculator()
    _results = rc.compute_results(_readings)
    rp = ResultProcessor()
    rp.produce_report(_results)
