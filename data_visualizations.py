import data_cleanup
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import language_family as langs
from scipy.stats import chisquare


def bar_plot(data, field):
    """
    Plots a generic bar plot by count for the given field.
    """
    sns.set()
    sns.catplot(x=str(field), kind='count', data=data, color='b', height=5)
    plt.xticks(rotation=-45, fontsize='medium', horizontalalignment='left')
    plt.title('Plot of frequency of each ' + str(field))
    plt.show()


def compare_plot(data, x_name, y_name):
    """
    Plots a violin plot with each categorical option on the
    x-axis and a numerical value (usually age) on the y-axis,
    as well as a control plot of just the y-axis column to
    compare the others to.
    """
    sns.set()
    # Plots observed variable
    fig, [ax1, ax2] = plt.subplots(2)
    sns.violinplot(x=x_name, y=y_name, data=data, ax=ax1, width=.8)
    ax1.set_title('Plot of frequency of ' + str(x_name) + ' by ' + str(y_name))
    ax1.tick_params(axis='x', labelrotation=-45, labelsize='small',
                    labelleft=True)
    # Plots control
    if len(data[x_name].unique()) <= 1:
        sns.violinplot(x=x_name, y=y_name, data=data, ax=ax2, width=.8)
    else:
        sns.violinplot(y=y_name, data=data, ax=ax2,
                       width=(.8 / (len(data[x_name].unique()) - 1)))
    plt.xticks(rotation=-45, fontsize='medium', horizontalalignment='left')
    ax2.set_title('Control plot of sample ' + str(y_name))
    plt.tight_layout()
    plt.show()


def prop_plot(data, cat_names, props):
    """
    Shows a bar plot of the proportion props for each category in
    cat_names, with the titles and labels specified in the function.
    """
    sns.set()
    sns.catplot(data=data, x=cat_names, y=props, kind='bar', color='b')
    plt.xticks(rotation=-45, fontsize='medium', horizontalalignment='left')
    plt.title('Plot of proportion of speakers in each language family who ' +
              cat_names)
    plt.xlabel('Language Family')
    plt.ylabel('Proportion of Speakers')
    plt.show()


def get_proportions(data, cat_field_name, observed_field_name, true_cond):
    """
    Returns a dataframe which, for each option in the cat_field_name column
    of data, holds the proportion of times rows in that category meet the
    specified truth condition in the observed_field_name column of data.
    Does NOT divide by household.
    """
    proportions = pd.DataFrame()
    categories = []
    props = []
    # For each option of the cat_field
    for item in data[cat_field_name].astype(str).unique():
        # Get the proportion of times its entry in observed_field
        # meets true_cond
        temp = data[data[cat_field_name].astype(str) == str(item)]
        total = len(temp)
        observed = len(temp[temp[observed_field_name
                                 ].astype(str) == str(true_cond)])
        # Appends the name and ratio to their respective lists
        categories.append(str(item))
        props.append(observed / total)
    proportions['Categories'] = categories
    proportions['Proportions'] = props
    return proportions


def exclude_english(data, fields, key):
    """
    exclude_english() takes a dataframe and a list of field names
    and returns a copy of the dataframe with the English values
    replaced by Nan, provided it recognizes and has a rule for that field.
    """
    copy = data
    if 'HHLANP' in fields:
        copy['HHLANP_noEnglish'] = data['HHLANP'].replace(key['9500.0'],
                                                          np.nan)
    if 'HHL' in fields:
        copy['HHL_noEnglish'] = copy['HHL'].replace('English only', np.nan)
    if 'LANP' in fields:
        copy['LANP_noEnglish'] = copy['LANP'].replace(key['9999.0'], np.nan)
    if 'HHLANP_uncoded' in fields:
        copy['HHLANP_uncoded'] = copy['HHLANP_uncoded'
                                      ].astype(str).replace(('English or'
                                                             + 'Unspecified'
                                                             ), np.nan)
    return copy


def chisquare_prep(data, cat_field_name, cond_field_name, true_cond):
    """
    Performs a Chi-Square Goodness of Fit test on the members of
    the provided field of data which fit the provided condition.
    """
    # Prepare data for analysis
    observed = []
    expected = []
    copy = data[data[cat_field_name].astype(str) != 'nan']
    print('Minus nan: ' + str(len(copy[cat_field_name
                                       ])), str(copy[cat_field_name].unique()))
    copy = copy[copy[cat_field_name].astype(str) != 'English or Unspecified']
    # print('Big total: ' + str(len(data[cat_field_name])))
    total = len(copy[cat_field_name])
    # print('Small total: ' + str(total))
    for item in copy[cat_field_name].astype(str).unique():
        if str(item) == 'nan' or str(item) == 'English or Unspecified':
            print(':T')
        else:
            temp = copy[copy[cat_field_name].astype(str) == str(item)]
            # Observed = count of x language speakers which meet condition
            observed.append(len(temp[temp[cond_field_name
                                          ].astype(str) == str(true_cond)]))
            # Expected = row total * column total / total
            expected.append(len(temp) * len(copy[copy[cond_field_name]
                                                 == true_cond]) /
                            total)
    return chisquare(f_obs=observed, f_exp=expected)


def main():
    """
    Main runs the analysis.
    """
    # Load in and clean data and language keys
    all_indiv = pd.read_csv('psam_p53.csv')
    all_household = pd.read_csv('psam_h53.csv')
    data = data_cleanup.load_data(all_household, all_indiv)
    data = data_cleanup.recode(data)
    lang_key = data_cleanup.import_lang_key('language_recode.txt')
    language_families = langs.FamilyGroup()
    language_families.import_families('shortened_fam_labels.txt')

    # Create optional data filters
    filtered_data = exclude_english(data, ['HHLANP_uncoded', 'HHL', 'LANP'],
                                    lang_key)
    asian_data = data[(data['LANP_uncoded'].astype(str) == 'Mongolic') |
                      (data['LANP_uncoded'].astype(str) == 'Austroasiatic') |
                      (data['LANP_uncoded'].astype(str) == 'Sino-Tibetan') |
                      (data['LANP_uncoded'].astype(str) ==
                       'Kra-Dai+As. isolates') |
                      (data['LANP_uncoded'].astype(str) == 'Indo-Iranian') |
                      (data['LANP_uncoded'].astype(str) == 'Dravidian')]

    # Violin plots
    compare_plot(filtered_data, 'HHLANP_uncoded', 'AGEP')
    compare_plot(filtered_data, 'HHL', 'AGEP')

    # Gets proportions
    props_HHLANP_LNGI = get_proportions(filtered_data, 'HHLANP_uncoded',
                                        'LNGI', True)
    props_HHL_LNGI = get_proportions(filtered_data, 'HHL', 'LNGI', True)
    props_LANP_LNGI_asia = get_proportions(asian_data, 'LANP_uncoded',
                                           'LNGI', True)
    props_HHL_PAP = get_proportions(filtered_data, 'HHL', 'PAP', True)
    props_LANP_PAP = get_proportions(filtered_data, 'LANP_uncoded', 'PAP',
                                     True)

    # Plots proportions
    prop_plot(props_HHL_LNGI, 'Categories', 'Proportions')
    prop_plot(props_HHLANP_LNGI, 'Categories', 'Proportions')
    prop_plot(props_LANP_LNGI_asia, 'Categories', 'Proportions')
    prop_plot(props_HHL_PAP, 'Categories', 'Proportions')
    prop_plot(props_LANP_PAP, 'Categories', 'Proportions')

    # Prints Chi-Square tests
    print(str(props_HHLANP_LNGI['Proportions'].mean()),
          str(props_HHL_LNGI['Proportions'].mean()))
    print(chisquare_prep(filtered_data, 'LANP_uncoded', 'LNGI', True))
    print(chisquare_prep(asian_data, 'LANP_uncoded', 'LNGI', True))
    print(chisquare_prep(filtered_data, 'HHL', 'PAP', True))


if __name__ == '__main__':
    main()
