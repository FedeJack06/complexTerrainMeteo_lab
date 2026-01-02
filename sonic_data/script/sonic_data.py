import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import core as core
import pre_processing as pre_processing
import frame as frame
import matplotlib.dates as mdates

# data import
path_input = '../ES3_10_02_2012_cut/ES3_sonic_05_2012-10-02.csv'
ES3_10m_raw= pd.read_csv(path_input, sep=",", header=0)
ES3_10m_raw["Time"] = pd.to_datetime(ES3_10m_raw["Time"]) #set the timestamp column as index
ES3_10m_raw.set_index("Time", inplace=True)