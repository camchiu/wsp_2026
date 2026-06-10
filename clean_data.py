import pandas as pd
import numpy as np

### CLEAN FITBIT DATA ###
path = "Fitabase Data 4.12.16-5.12.16/"

# activity data
activity = pd.read_csv(path + "dailyActivity_merged.csv")
activity = activity[["Id", "ActivityDate", "TotalSteps", "TotalDistance", "Calories", "SedentaryMinutes"]]

activity = activity.rename(columns = {"Id": "ID",
                                      "ActivityDate": "Date",
                                      "TotalSteps": "Steps",
                                      "TotalDistance": "Distance_miles",
                                      "Calories": "Calories_burned",
                                      "SedentaryMinutes": "time_sedentary_mins"})

activity["Date"] = pd.to_datetime(activity["Date"], format="%m/%d/%Y").dt.date

# sleep data
sleep = pd.read_csv(path + "sleepDay_merged.csv")
sleep = sleep[["Id", "Date", "TotalMinutesAsleep", "TotalTimeInBed"]]
sleep["Date"] = pd.to_datetime(sleep["SleepDay"], format="%m/%d/%Y %I:%M:%S %p").dt.date

sleep = sleep.rename(columns = {"Id": "ID",
                                "TotalMinutesAsleep": "sleep_minutes",
                                "TotalTimeInBed": "inbed_minutes"})

# merge data
fitbit = pd.merge(activity, sleep, on = ["ID", "Date"], how = "inner")

fitbit["sleep_hours"] = fitbit["sleep_minutes"] / 60
fitbit["inbed_hours"] = fitbit["inbed_minutes"] / 60

fitbit["sleep_efficiency"] = (fitbit["sleep_minutes"] / fitbit["inbed_minutes"])

fitbit = fitbit[(fitbit["sleep_hours"].between(1, 15)) & 
                (fitbit["sleep_efficiency"].between(0, 1)) & 
                (fitbit["Steps"] >= 0)]

# reorder columns
fitbit = fitbit[["ID", "Date", "sleep_hours", "inbed_hours", "sleep_efficiency",
                 "Steps", "Distance_miles", "Calories_burned", "time_sedentary_mins"]]
# rename id to person
id_map = {id_: f"p{i+1}" for i, id_ in enumerate(sorted(fitbit["ID"].unique()))}
fitbit["ID"] = fitbit["ID"].map(id_map)

# convert date to day
fitbit["Date"] = pd.to_datetime(fitbit["Date"])
start_date = fitbit["Date"].min()
fitbit["Day"] = (fitbit["Date"] - start_date).dt.days + 1
fitbit = fitbit.drop(columns=["Date"])

# save cleaned data
fitbit.to_csv("fitbit_sleep.csv", index=False)

### BRFSS data ###
df = pd.read_sas("LLCP2022.XPT ")

# columns to keep
cols = ["_STATE",        # state    
        "SLEPTIM1",      # sleep hours
        "GENHLTH",       # general health
        "PHYSHLTH",      # poor physical health days
        "MENTHLTH",      # poor mental health days
        "EXERANY2",      # exercised recently
        "_BMI5",         # BMI * 100
        "ADDEPEV3",      # depression diagnosis
        "_AGE80",        # age
        "_SEX",          # sex
        "INCOME3",       # income category
        "EDUCA",         # education
        "SMOKDAY2",      # smoking
        "DRNKANY6"       # alcohol frequency
]

sleep = df[cols].copy()
sleep.replace([7, 77, 777, 88, 9, 99, 999, 9999], np.nan, inplace = True)

# clean
sleep["SLEPTIM1"] = pd.to_numeric(sleep["SLEPTIM1"], errors="coerce")
sleep.loc[~sleep["SLEPTIM1"].between(1, 24), "SLEPTIM1"] = np.nan

# rename columns
sleep = sleep.rename(columns = {"_STATE": "state",
                                "SLEPTIM1": "sleep_hours",
                                "GENHLTH": "general_health",
                                "PHYSHLTH": "poor_physical_days",
                                "MENTHLTH": "poor_mental_days",
                                "EXERANY2": "exercise",
                                "_AGE80": "age",
                                "_SEX": "sex",
                                "_BMI5": "bmi",
                                "INCOME3": "income",
                                "EDUCA": "education",
                                "SMOKDAY2": "smoking",
                                "DRNKANY6": "alcohol_use",
                                "ADDEPEV3": "depression"})

sleep["bmi"] = sleep["bmi"] / 100
sleep.loc[~sleep["bmi"].between(10, 80), "bmi"] = np.nan

sleep["sex"] = sleep["sex"].map({ 1: "Male", 2: "Female"})
sleep["exercise"] = sleep["exercise"].map({1: "Yes", 2: "No"})

sleep["alcohol_use"] = sleep["alcohol_use"].map({1: "Yes", 2: "No"})

sleep["depression"] = sleep["depression"].map({1: "Yes", 2: "No"})

state_map = {
    1: "Alabama",
    2: "Alaska",
    4: "Arizona",
    5: "Arkansas",
    6: "California",
    8: "Colorado",
    9: "Connecticut",
    10: "Delaware",
    11: "District of Columbia",
    12: "Florida",
    13: "Georgia",
    15: "Hawaii",
    16: "Idaho",
    17: "Illinois",
    18: "Indiana",
    19: "Iowa",
    20: "Kansas",
    21: "Kentucky",
    22: "Louisiana",
    23: "Maine",
    24: "Maryland",
    25: "Massachusetts",
    26: "Michigan",
    27: "Minnesota",
    28: "Mississippi",
    29: "Missouri",
    30: "Montana",
    31: "Nebraska",
    32: "Nevada",
    33: "New Hampshire",
    34: "New Jersey",
    35: "New Mexico",
    36: "New York",
    37: "North Carolina",
    38: "North Dakota",
    39: "Ohio",
    40: "Oklahoma",
    41: "Oregon",
    42: "Pennsylvania",
    44: "Rhode Island",
    45: "South Carolina",
    46: "South Dakota",
    47: "Tennessee",
    48: "Texas",
    49: "Utah",
    50: "Vermont",
    51: "Virginia",
    53: "Washington",
    54: "West Virginia",
    55: "Wisconsin",
    56: "Wyoming",
    66: "Guam",
    72: "Puerto Rico",
    78: "U.S. Virgin Islands"
}

sleep["state"] = sleep["state"].map(state_map)
sleep = sleep.dropna(subset = ["sleep_hours"])

sleep.to_csv("brfss_sleep_clean.csv", index = False)