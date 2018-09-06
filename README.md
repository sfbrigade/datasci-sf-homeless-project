![](datasciheader.png)
# CTA-NorCal Homeless Program Outcomes Analysis

## HMIS Analytics 

Members of the [Data Science Working Group](https://github.com/sfbrigade/data-science-wg) at Code for San Francisco have been charged with answering the [Community Technology Alliance’s](https://ctagroup.org/) prompt about homelessness programs.

## Prompt
What variables best predict whether an individual is categorized as ‘in permanent housing’ as an outcome, by population segment:
- Veterans
- Chronically Homeless
- Continuously Homeless
- Has Disabling Condition
- Domestic Violence Victim
- Male/Female
- Latino/Non-Latino

## Data
Data is in [HMIS format](https://www.hudexchange.info/programs/hmis/), a data standard defined by the US Department of Housing and Urban Development 

## Results
View the [HMIS Data Science Study Presentation](https://docs.google.com/presentation/d/1VqjvqFESZXEjwaNqLywOfcIeyVFPAKO_So9wIdsvWgs/edit?usp=sharing) for a summary of our findings

## Featured Notebooks
- [Load and clean the data](https://github.com/sfbrigade/datasci-sf-homeless-project/blob/master/notebooks/load_data_example_v2.ipynb)
- [Explore the data](https://github.com/sfbrigade/datasci-sf-homeless-project/blob/master/notebooks/2016-10-19_mvm_exploration.ipynb)
- [Feature engineering to prepare input variables](https://github.com/sfbrigade/datasci-sf-homeless-project/blob/master/notebooks/2016-12-05_mvm_one_hot_encode.ipynb)
- [Make outcome predictions with logistic regression model](https://github.com/warmlogic/datasci-sf-homeless-project/blob/master/notebooks/2017-01-22_mvm_permanent_housing_predictions.ipynb)

## Setup

Install Jupyter Notebook; this is most easily done by installing Anaconda: https://www.continuum.io/downloads

Install seaborn. To do this in a new conda environment:  
```conda create --name datasci seaborn```

To deactivate/activate the environment:  
```source deactivate datasci```  
```source activate datasci```

## Get Started

1. Fork this repository and clone it locally.
2. Locate the dataset (pinned in #datasci-homeless on Slack).
3. Run ```jupyter notebook```
4. Navigate to notebooks/load_data_example_v2.ipynb to start exploring the data.

Additional information on completed and open items can be found in the pinned documents in #datasci-homeless.
