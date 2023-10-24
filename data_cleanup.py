import numpy as np
import language_family as langs
print("Imports done")


def load_data(household, indiv):
    """
    Loads in and merges the datasets, and returns the result after
    dropping any row or column that is completely empty.
    """
    smaller_household = household[['SERIALNO', 'LNGI', 'HHLANP', 'HHL']]
    smaller_indiv = indiv[['SERIALNO', 'SPORDER', 'AGEP',
                           'LANP', 'LANX', 'PAP']]
    data = smaller_household.merge(smaller_indiv, left_on='SERIALNO',
                                   right_on='SERIALNO', how='inner')
    data = data.dropna(how='all')
    return data


def recode(data):
    """
    Recodes all categorical variables from floats to
    descriptive labels.
    """

    # Recodes Household Language column (HHL).
    # HHL is the primary household language as categorized
    # by the survey.
    ser = data['HHL'].replace(1.0, 'English only')
    ser = ser.replace(2.0, 'Spanish')
    ser = ser.replace(3.0, 'Other Indo-European')
    ser = ser.replace(4.0, 'Asian and Pacific Island')
    ser = ser.replace(5.0, 'All other languages')
    data['HHL'] = ser

    # Recodes Precise Household Language column (HHLANP).
    # HHLANP is the primary household language per language.
    key = import_lang_key('language_recode.txt')
    data = recode_language(data, 'HHLANP', key)

    # Recodes Personal Language Spoken at Home column (LANP).
    # LANP is the precise language the respondent marked that
    # they speak at home.
    data = recode_language(data, 'LANP', key)

    # Recodes LNGI column.
    # If LNGI is True, the household is linguistically isolated, which
    # means that no member of the household 14 or over speaks
    # English 'very well' or better.
    ser = data['LNGI'].replace(0.0, np.nan)
    ser = ser.replace(1.0, False)
    ser = ser.replace(2.0, True)
    data['LNGI'] = ser

    # Recodes LANX column.
    # If LANX is True, respondent speaks a language other than
    # English at home.
    ser = data['LANX'].replace(0.0, np.nan)
    ser = ser.replace(1.0, True)
    ser = ser.replace(2.0, False)
    data['LANX'] = ser

    # Recodes -1 in Public Assistance Income (PAP) column as False.
    # Otherwise, the number in PAP is the amount of public assistance
    # income that person receives, so it sets PAP to True.
    data.loc[(data['PAP'] > 0.0), 'PAP'] = True
    data.loc[(data['PAP'] <= 0.0), 'PAP'] = False
    return data


def import_lang_key(file_name):
    """
    import_lang_key builds a dictionary from a file of the
    format "id, name" to associate language id numbers to
    their names.
    """
    # Reads in the individual languages as a list of tuples
    with open(file_name) as f:
        lines = [tuple(map(str, i.strip().split(','))) for i in f]
        # lang_key = {'1.0': 'English only'}
        lang_key = {}
    # Processes the individual languages into a dictionary
    for line in lines:
        lang_key[(line[0] + '.0')] = line[1]

    return lang_key


def classify_langs(data, group_key, column_name):
    """
    classify_langs goes through all values in the provided
    language column and returns a version of the series where
    id numbers are replaced by linguistic groups.
    """
    temp = data[column_name].dropna().astype(int)
    tokens = temp.unique()
    keys = []
    for item in tokens:
        recode = group_key.classify(item)
        temp = temp.replace(item, recode)
        keys.append(recode)
    return temp


def recode_language(data, col, lang_key):
    """
    recode_language replaces each non-Nan value in a column of a dataframe
    with its associated value in the dictionary passed to it as lang_key.
    """
    group_key = langs.FamilyGroup()
    group_key.import_families('shortened_fam_labels.txt')
    data[col + '_uncoded'] = data[col]
    data[col] = data[col].astype(str).replace(value=None, regex=lang_key)
    data[col] = data[col].replace('nan', np.nan)
    data[col + '_uncoded'] = classify_langs(data, group_key, col + '_uncoded')

    return data
