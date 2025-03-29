### Takes a raw tick data as exported by meta trader and converts it into csv ML tools can work with
from datetime import datetime

def addForRange(_range, formatted_lines, _data):
    split = _data.split(',')
    #oPos = float(split[2])
    #cPos = float(split[5])
    # get RSI_range

    counter = 0
    high_close = []
    low_close = []
    while counter < int(_range):
        cPos = float(str(formatted_lines[-1 - counter]).split(',')[5])
        cPosPrev = float(str(formatted_lines[-2 - counter]).split(',')[5])
        val = cPos - cPosPrev
        if val < 0:
            low_close.append(val)
        else:
            high_close.append(val)
        counter+=1
    normalizer = 0.0000001
    try:
        avg_gain = sum(high_close) / len(high_close)
    except ZeroDivisionError:
        avg_gain = normalizer
    try:
        avg_loss = sum(low_close) / len(low_close)
    except ZeroDivisionError:
        avg_loss = normalizer
    rs = (avg_gain/avg_loss) * -1
    rsi = int(10 - (10/(1+rs)))    # calculate rsi with rs
    _data = f"{_data},{rsi}"
    return _data
    

def appendRSI(_data, _ranges, formatted_lines):
    for _ in _ranges:
        _data = addForRange(_, formatted_lines, _data)    
    return _data

def get_day_of_week(date_str, date_format="%Y-%m-%d"):
    date_obj = datetime.strptime(date_str, date_format)
    return date_obj.weekday()

def getTrainDataFromLines(_formatted_lines):    # this function takes the formatted lines, do all maths and returns valid training data
    rsiRange = [3, 6, 12, 24, 48, 96, 192, 348, 768, 1536]
    return_data = []
    # write and append header
    toAppend = ''
    for _ in rsiRange:
        toAppend += f',<RSI_{_}>'
    toAppend += ",<TIMETD>, <DOW>"
    return_data.append(f"{_formatted_lines[0]}{toAppend}") # append header

    
    rsiCounter = 0
    # add all rsi for each line
    for _ in _formatted_lines[1537:]:
        _ = appendRSI(_ , rsiRange , _formatted_lines[1+rsiCounter:1538+rsiCounter]) # append rsi ranging from, half a day to a year.
        return_data.append(_)
        rsiCounter+=1

    # add time TD
    counter = 1
    for _ in return_data[1:]:
        _data = _
        timeTD = int(_data.split(',')[1][0:2])  # get time TD
        date_str = _data.split(',')[0]
        dow = get_day_of_week(date_str, date_format="%Y.%m.%d") #get day of week
        return_data[counter] = f"{_}, {timeTD}, {dow}"
        counter +=1

    #return full data
    return return_data


# Specify the input and output file paths
# input files can exists anywhere, but you shoul store tham in the rawCharts folder for readability
def convert(path_to_raw_chart):
    print("convert initialized... writing file chart")
    input_file = path_to_raw_chart # path as str
    outputE = path_to_raw_chart.split('/')[-1]
    try:
        fineOutput = f"fineCharts/{outputE}"   # save in fineCharts as main.py
        tDataOutput = f"trainingData/{outputE}"
        # Read the data from the input file
        with open(input_file, 'r') as file: # read fine
            lines = file.readlines()

        # Add commas to each line
        formatted_lines = []    # store lines
        for line in lines:
            formatted_lines.append(','.join(line.split()))  # loop through lines and split all by space, join back with ',' instead of space

        # Write the formatted data to the output file
        with open(fineOutput, 'w') as file:    
            file.write('\n'.join(formatted_lines))      # write list as new file

        print(f"Formatted data has been written to {fineOutput}")  # alert success
        print("Generating training data...")

        training_data = getTrainDataFromLines(formatted_lines)  # generate training data to match 

        with open(tDataOutput , 'w') as file:
            file.write('\n'.join(training_data))
        
        print(f"Training data written to {tDataOutput}")

    except Exception as e:  # if error, print error
        print(f"Failed to write. Error: \n\t{e}")

        return 1