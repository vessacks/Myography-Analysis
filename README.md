This script imports myography experiment data generated in labchart and exported as a CSV to the "data" folder. It can analyze multiple experimental files at once. 
Then it dentifies the peaks in muscle tension indicated a drug was added
Then it calculates the mean tension and AUC in between peaks 
Then it generates graphs of the identified peaks for manual inspection and CSVs of the peak-to-peak data
All output is stored in the output folder
Note: the parameters are tuned for a particular myography rig and mouse blood vessel. These parameters would need to be retuned for use in other rigs or with other types of blood vessels. 
