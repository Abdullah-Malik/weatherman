import os
import argparse
import sys
import termcolor
from termcolor import colored

parser = argparse.ArgumentParser()
parser.add_argument('-a', nargs='?', default="", type=str)
parser.add_argument('-e', nargs='?', default="", type=str)
parser.add_argument('-c', nargs='?', default="", type=str)
args = parser.parse_args()

num_to_month = ['Jan', 'Feb', 'Mar','Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
num_to_full_month_name = ['January', 'February', 'March','April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

class FileReader:
    def __init__(self):
        pass
        
    def get_file_path(self, date):
        year, month = date.split('/')
        path = './weatherfiles/Murree_weather_'+str(year)+'_'+ num_to_month[int(month)-1] +'.txt'

        if os.path.isfile(path):
            return [path]
        else:
            print("File for", date, "does not exist")

    def get_all_filenames(self, date):
        dir_path = '/home/abdullahmalik/Desktop/weatherman/weatherfiles'
        year_name = 'Murree_weather_'+str(date)
        all_file_names = [os.path.join(dir_path, filename) for filename in os.listdir(dir_path) \
                                                                if os.path.isfile(os.path.join(dir_path, filename))  \
                                                                        and filename.startswith(year_name)]
        return all_file_names

    def check_int(self, val):
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            return val

    def readFiles(self, filename_list):
        readings = []
        file_data = []
        
        for file in filename_list:
            file_lines = open(file, 'r').readlines()
            file_data = [[self.check_int(val) for val in line.split(',') ] for line in file_lines[1:] ]
            readings.extend(file_data)
        return readings


    def process_files(self):
        weather_readings = {}
        if args.c is not None:
            weather_readings['c'] =  self.readFiles(self.get_file_path(args.c))
        
        if args.a :
            weather_readings['a'] = self.readFiles(self.get_file_path(args.a))

        if args.e :
           weather_readings['e'] = self.readFiles(self.get_all_filenames(args.e))

        return weather_readings

class ResultCalculator:
    def __init__(self):
        pass

    def check_values(self, a, b):
        if a and b:
            return True

    def process_readings_as_per_flag(self, readings, flag):

        if flag == 'c':
            max_min_temp = []
            for line in readings:
                if self.check_values(line[1], line[3]):
                    max_min_temp.append((line[1], line[3]))
            return {"daily_temperatures": max_min_temp}

        elif flag == 'a':
            
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

            average_mean_humidity = average_mean_humidity/len(readings)
            average_max_temp = average_max_temp/len(readings)
            average_min_temp = average_min_temp/len(readings)


            return {"avg_max_temp": average_max_temp, "avg_min_temp": average_min_temp, "mean_humidity": average_mean_humidity}

        elif flag == 'e':
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

                if max_temp:
                    if max_temperature < max_temp:
                        max_temperature = max_temp
                        max_temperature_day = day

                if min_temp: 
                    if min_temperature > min_temp:
                        min_temperature = min_temp
                        min_temperature_day = day
                
                if max_humid:
                    if max_humidity < max_humid:
                        max_humidity = max_humid
                        max_humidity_day = day

        return {"max_temp": max_temperature, "max_day": max_temperature_day,
                    "min_temp": min_temperature, "min_day": min_temperature_day,
                    "max_humidity": max_humidity, "humid_day": max_humidity_day}



    def compute_results(self, weather_readings):
        result_dict = {}
        for flag, all_reading in weather_readings.items():
            result_dict[flag] = self.process_readings_as_per_flag(all_reading, flag)
        

        return result_dict

class ResultProcessor:
    def __init__(self) -> None:
        pass

    def check_values(self, a, b):
        if a and b:
            return True

    def get_day(self, date):
        
        year, month, day = date.split('-')
        month = int(month) 
        return num_to_full_month_name[month-1] + " " + str(day)

    def produce_report(self, weather_results):
        for flag, results in weather_results.items():
            if flag == 'c':
                print("Report for c")
                for i, tup in enumerate(results["daily_temperatures"]):
                    max, min = tup
                    
                    if self.check_values(max, min):
                        blues = '+'*min
                        reds = '+'*(max-min)
                        
                        print(str(i+1)+" "+colored(blues, 'blue')+colored(reds, 'red')+ str(min)+'C - '+str(max)+'C')
                print()
            elif flag == 'a':
                print("Report for a")
                print("Highest Average: "+ str(results["avg_max_temp"]) + "C")
                print("Lowest Average: " + str(results["avg_min_temp"]) + "C")
                print("Average Mean Humidity: " + str(results["mean_humidity"]) + "%")
                print()

            
            elif flag == 'e':
                print("Report for e")
                print("Highest: " + str(results["max_temp"]) + "C on " + self.get_day(results["max_day"]))
                print("Lowest: " + str(results["min_temp"]) + "C on " + self.get_day(results["min_day"]))
                print("Humidity: " + str(results["max_humidity"]) + "% on " + self.get_day(results["humid_day"]))


 
if __name__ == "__main__":
    weather_readings = {}
    fr = FileReader()
    weather_readings = fr.process_files()
    rc = ResultCalculator()
    weather_results = rc.compute_results(weather_readings)
    rp = ResultProcessor()
    rp.produce_report(weather_results)
