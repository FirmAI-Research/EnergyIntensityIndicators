import pandas as pd
import numpy as np
from sklearn import linear_model
from functools import reduce
import os
from datetime import date
import matplotlib.pyplot as plt
import seaborn
import plotly.graph_objects as go
import plotly.express as px


class MultiplicativeLMDI():

    def __init__(self, energy_data=None, energy_shares=None, base_year=None, end_year=None, total_label=None, lmdi_type=None):
        self.energy_data = energy_data
        self.energy_shares = energy_shares
        self.base_year = base_year
        self.end_year = end_year
        self.total_label = total_label
        self.lmdi_type = lmdi_type

    def log_mean_divisia_weights(self):
        """Calculate log mean weights where T = t, 0 = t-1

        Multiplicative model uses the LMDI-II model because 'the weights...sum[] to unity, a 
        desirable property in index construction.' (Ang, B.W., 2015. LMDI decomposition approach: A guide for 
                                        implementation. Energy Policy 86, 233-238.).
        """

        log_mean_weights = pd.DataFrame(index=self.energy_data.index)
        for col in self.energy_shares.columns: 
            self.energy_shares[f"{col}_shift"] = self.energy_shares[col].shift(periods=1, axis='index', fill_value=0)
            # apply generally not preferred for row-wise operations but?
            log_mean_weights[f'log_mean_weights_{col}'] = self.energy_shares.apply(lambda row: \
                                                          self.logarithmic_average(row[col], row[f"{col}_shift"]), axis=1) 
        sum_log_mean_shares = log_mean_weights.sum(axis=1)
        log_mean_weights_normalized = log_mean_weights.divide(sum_log_mean_shares.values.reshape(len(sum_log_mean_shares), 1))
        return log_mean_weights_normalized

    @staticmethod
    def logarithmic_average(x, y):
        """The logarithmic average of two positive numbers x and y
        """        
        try:
            x = float(x)
            y = float(y)
        except TypeError:
            L = np.nan
            return L  
                 
        if x > 0 and y > 0:
            if x != y:
                difference = x - y
                log_difference = np.log(x / y)
                L = difference / log_difference
            else:
                L = x
        else: 
            L = np.nan

        return L
    
    def compute_index(self, component, base_year_):
        """
        """         
        index = pd.DataFrame(index=component.index, columns=['index'])
        for y in component.index:
            if y == min(component.index):
                index.loc[y, 'index'] = 1
            else:
                if component.loc[y] == np.nan:
                    index.loc[y, 'index'] = index.loc[y - 1, 'index']

                else:
                    index.loc[y, 'index'] = index.loc[y - 1, 'index'] * component.loc[y]

        index = index.fillna(1)    
        index_normalized = index.divide(index.loc[base_year_]) # 1985=1
        return index_normalized 

    def decomposition(self, ASI):
        ASI_df = pd.DataFrame.from_dict(data=ASI, orient='columns')
        print('ASI_df:\n', ASI_df)
        results = ASI_df.apply(lambda col: np.exp(col), axis=1)
        print(' log ASI_df:\n', results)

        for col in results.columns:
            results[col] = self.compute_index(results[col], self.base_year)
        print('indexed log ASI df:\n', results)
        results['effect'] = results.product(axis=1)
        print("results['effect']:\n", results['effect'])
        print('all results df:\n', results)
        results["@filter|Measure|BaseYear"] = self.base_year
        return results

    @staticmethod
    def visualizations(data, base_year, end_year, loa, model, energy_type, *lines_to_plot): # path
        plt.style.use('seaborn-darkgrid')
        palette = plt.get_cmap('Set2')

        for i, l in enumerate(lines_to_plot):
            label_ = l.replace("_", " ").capitalize()
            plt.plot(data['@timeseries|Year'], data[l], marker='', color=palette(i), linewidth=1, alpha=0.9, label=label_)
        
        loa = [l_.replace("_", " ") for l_ in loa]
        loa = " /".join(loa)
        title = loa + f" {model.capitalize()}" + f" {energy_type.capitalize()} {base_year}" 
        plt.title(title, fontsize=12, fontweight=0)
        plt.xlabel('Year')
        # plt.ylabel('')
        plt.legend(loc=2, ncol=2)
        plt.show()
        # plt.save(f"{path}/{title}.png")