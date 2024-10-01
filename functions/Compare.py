import pandas as pd
import matplotlib.pyplot as plt


def compare_sim_vs_sim_var(df1, df2, name1, name2, var, uniqueID):
    merged_df = pd.merge(df1, df2, on=uniqueID, suffixes=('_' + name1, '_' + name2))

    # Check if the variable is a date column
    if pd.api.types.is_datetime64_any_dtype(merged_df[var + '_' + name1]) or pd.api.types.is_datetime64_any_dtype(merged_df[var + '_' + name2]):
        # Convert the dates to day of the year (ignoring the year)
        merged_df[var + '_' + name1] = pd.to_datetime(merged_df[var + '_' + name1]).dt.dayofyear
        merged_df[var + '_' + name2] = pd.to_datetime(merged_df[var + '_' + name2]).dt.dayofyear

    plt.figure(figsize=(8, 6))

    # Create a mapping from TRT_NAME to colors
    unique_ids = merged_df['TRT_NAME'].unique()
    colors = plt.cm.get_cmap('viridis', len(unique_ids))
    color_mapping = {cul_id: colors(i) for i, cul_id in enumerate(unique_ids)}

    # Plot with the mapped colors
    plt.scatter(merged_df[var + '_' + name1], merged_df[var + '_' + name2],
                color=[color_mapping[c] for c in merged_df['TRT_NAME']], alpha=0.6)

    # Plot the 1:1 line
    max_value = max(merged_df[var + '_' + name1].max(), merged_df[var + '_' + name2].max())
    min_value = min(merged_df[var + '_' + name1].min(), merged_df[var + '_' + name2].min())
    plt.plot([min_value, max_value], [min_value, max_value], color='r', linestyle='--', label='1:1 Line')

    plt.xlabel(name1 )
    plt.ylabel(name2 )
    plt.title('Compare ' + var)
    plt.grid(True)

    # Create custom legend
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_mapping[c], markersize=10) for c in
               unique_ids]
    plt.legend(handles, unique_ids, title='TRT_NAME')


def compare_sim_vs_sim_list(df1, df2, name1, name2, listVar, uniqueID):
    for var in listVar:
        compare_sim_vs_sim_var(df1, df2, name1, name2, var, uniqueID)
    plt.show()
    merged_df = pd.merge(df1, df2, on=uniqueID, suffixes=('_' + name1, '_' + name2))
    return(merged_df)