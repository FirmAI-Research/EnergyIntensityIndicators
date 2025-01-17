import numpy as np

from EnergyIntensityIndicators.utilities.dataframe_utilities \
    import DFUtilities as df_utils


class TestingUtilities:

    acceptable_pct_difference = 0.05

    def pct_diff(self, pnnl_data, eii_data):
        if pnnl_data.empty or eii_data.empty:
            return False
        elif pnnl_data.empty and eii_data.empty:
            return True
        else:
            pnnl_data, eii_data = df_utils()\
                .ensure_same_indices(pnnl_data, eii_data)

            diff_df = pnnl_data.subtract(eii_data)
            diff_df_abs = np.absolute(diff_df)
            pct_diff = np.absolute(diff_df_abs.divide(pnnl_data))
            compare_df = pct_diff.fillna(0)\
                .apply(lambda col: col <= self.acceptable_pct_difference,
                       axis=1)
            return compare_df.all(axis=None)

    def pct_diff_bools_list(self, df_pairs_list):
        """Given pairs (tuples) of eii, pnnl dataframes, return a
        list of bools indicating whether the percent different
        between the dataframes are within the acceptable range
        """
        bools_list = []
        for eii, pnnl in df_pairs_list:
            pct_difference = self.pct_diff(pnnl, eii)
            bools_list.append(pct_difference)

        return bools_list


if __name__ == '__main__':
    pass
