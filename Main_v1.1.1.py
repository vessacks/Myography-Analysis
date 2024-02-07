#catherine data reader
#goal: identify peaks, average value between peaks, and the auc. 
#quality control: graphically represent where it's finding peaks so she can confirm it's working correctly.
#write the data to a csv when done, ideally with the graph as well.

#Note to catherine: to generate the data, you should go to "export" in labchart, select csv
#The mean_delta threshold, search window, and and peak_tick_sleep will need to be tuned by me
#if you downsample your data, you'll need to retune. Downsampling will make it run faster
#the peaks will be off by up to search_window ticks. Keep search window small to minimize this effect.
#limitation: if your peak is within the first search_window ticks, it won't be detected.this is because the rolling mean is undefined for the first search_window ticks.

#its including censored peaks. fix it

import pandas as pd
import os 
import matplotlib.pyplot as plt


#variables
working_directory = "C:\\Users\\username\\OneDrive - Imperial College London\\Documents\\Personal\\Projects\\Catherine myography peaking 2.4.24\\"
search_window = 3 #number of tick deltas examined for peak in sliding window
mean_delta_threshold = .009 #threshold for average slope across search window after which a peak is identified
peak_tick_sleep = 2 #how long to wait after discovering a peak to start looking for another one. 


#set directory
os.chdir(working_directory)

#search data directory for .csv files
file_list = []
for file in os.listdir(working_directory + "data"):
    if file.endswith(".csv"):
        file_list.append(file)

#you're dropping this early for loop because it wipes file name info needed for saving later

for file in file_list:
    df = pd.read_csv("data/"+file)
    df.columns = ["X", "Y"]



    #calculating first difference
    df["delta"] = df["Y"].diff().fillna(0)

    #calculating rolling mean of first different in search window
    df["rolling_mean"] = df["delta"].rolling(window=search_window).mean()
    #replace nans with zeros in df["rolling_mean"] caused by undefined first few terms
    df["rolling_mean"] = df["rolling_mean"].fillna(0)
    #note: this rolling mean will identify peaks offset by as many ticks as the search window. if that's an issue, you'll have to deal with it later



    #identify peaks
    df["peak"] = df["rolling_mean"] > mean_delta_threshold

    #clean up duplicate peaks
    #making as many 1 shifted censoring columns as there are peak tick sleep
    for i in range(peak_tick_sleep):
        df["censor" + str(i+1)] = df["peak"].shift(i+1, fill_value=False) #the plus 1 prevents censoring the first peak

    #combine the censoring columns to create the final censor column using a loop
    df["censor"] = False
    for i in range(peak_tick_sleep):
        df["censor"] = df["censor"] | df["censor" + str(i+1)]

    #drop the temporary columns
    for i in range(peak_tick_sleep):
        df = df.drop(columns=["censor" + str(i+1)])

    #apply the censor
    df["peak_censored"] = df["peak"] & ~df["censor"]

    #print(df.head())


    #split into single peak dfs
    # Step 1: Identify the indices where 'peak' is True
    peak_indices = df[df['peak_censored']].index.tolist()
    # Step 2: Split the DataFrame into multiple DataFrames based on the indices
    # Add the start and end indices to get first and last peak
    padded_peak_indices = [0] + peak_indices + [len(df)]
    # Using zip to create pairs of indices for splitting
    index_pairs = zip(padded_peak_indices[:-1], padded_peak_indices[1:])
    # Step 3: Split DataFrame into smaller DataFrames
    split_dfs = [df.iloc[start:end] for start, end in index_pairs]

    #iterate through the dfs, calculate values of interest, write into single peak_df
    peak_df= pd.DataFrame(columns=["start", "end", "mean", "auc"])
    for i, peak in enumerate(split_dfs):
        peak_df.loc[i, "start"] = peak["X"].iloc[0]
        peak_df.loc[i, "end"] = peak["X"].iloc[-1]
        peak_df.loc[i, "mean"] = peak["Y"].mean()
        peak_df.loc[i, "auc"] = peak["Y"].mean() *(peak["X"].iloc[-1] - peak["X"].iloc[0]) #AUC = mean * duration

    #write the peak_df to a csv
    peak_df.to_csv("output/"+file+"_peaks.csv")    

    #plot the data with peaks
    plt.clf()
    plt.plot(df["X"], df["Y"])
    #plotting uncensored peaks
    for x, peak in zip(df["X"], df["peak"]):
        if peak:  # This checks if the 'peak' column value is True for the row
            plt.axvline(x=x, color='r', linestyle='--') 
    #plotting censored peaks
    for x, peak in zip(df["X"], df["peak_censored"]):
        if peak:  # This checks if the 'peak' column value is True for the row
            plt.axvline(x=x, color='g', linestyle='-')
    #save the plot in output as a png
    plt.savefig("output/"+file+"_data_peaks.png")
    #plt.show()
    plt.clf()


    #plot the delta
    plt.plot(df["X"], df["delta"])
    #plotting uncensored peaks
    for x, peak in zip(df["X"], df["peak"]):
        if peak:  # This checks if the 'peak' column value is True for the row
            plt.axvline(x=x, color='r', linestyle='--') 
    #plotting censored peaks
    for x, peak in zip(df["X"], df["peak_censored"]):
        if peak:  # This checks if the 'peak' column value is True for the row
            plt.axvline(x=x, color='g', linestyle='-')
    #save the plot in output as a png
    plt.savefig("output/"+file+"_delta_peaks.png")
    #plt.show()
    plt.clf()

    #plot the rolling mean
    plt.plot(df["X"], df["rolling_mean"])
    #plotting uncensored peaks
    for x, peak in zip(df["X"], df["peak"]):
        if peak:  # This checks if the 'peak' column value is True for the row
            plt.axvline(x=x, color='r', linestyle='--') 
    #plotting censored peaks
    for x, peak in zip(df["X"], df["peak_censored"]):
        if peak:  # This checks if the 'peak' column value is True for the row
            plt.axvline(x=x, color='g', linestyle='-')
    #save the plot in output as a png
    plt.savefig("output/"+file+"_rolling_mean_peaks.png")
    #plt.show()
    plt.clf()
    
    print('completed file ' + file + ' with ' + str(len(peak_df)) + ' peaks')






print('bubba')
