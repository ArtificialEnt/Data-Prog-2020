class LanguageFamily:
    """
    Each LanguageFamily object represents a linguistic group-
    Indo-European languages, for example, or Austronesic languages.
    Each one has a name and a range of language ID numbers
    associated with it.
    """
    def __init__(self, name, min, max):
        """
        Initializes the LanguageFamily.
        """
        self._min = min
        self._max = max
        self._name = name

    def get_range(self):
        """
        Returns the range of language ids which qualify as part
        of the family.
        """
        return (self._min, self._max)

    def get_name(self):
        return self._name

    def get_min(self):
        return self._min

    def get_max(self):
        return self._max

    def equals(self, other):
        """
        Function to check whether a given language id is part of
        the language family.
        """
        if float(other) >= self._min and float(other) <= self._max:
            return True
        else:
            return False

    def __repr__(self):
        return self._name


class FamilyGroup:
    """
    Each FamilyGroup object represents a group of LanguageFamilies
    organized in a dictionary with their minimum number as the key,
    for easy retrieval.
    """
    def __init__(self, families={}):
        """
        Initializes the group.
        """
        self._families = {}
        self._families = families

    def add_family(self, family):
        """
        Adds a single LanguageFamily to the group.
        """
        self._families[str(family.get_min())] = family

    def import_families(self, file_name):
        """
        Imports a csv or txt file of the format min, max, name
        as LanguageFamily objects and adds them to the group.
        """

        # Reads in the language ranges as a list of thruples.
        with open(file_name) as f:
            lines = [tuple(map(str, i.strip().split(', '))) for i in f]

        # Processes the language ranges into a dictionary
        for line in lines:
            low, high, name = line
            self._families[str(low)] = LanguageFamily(name, float(low),
                                                      float(high))

    def classify(self, language_id):
        """
        Classifies the given language id number as a member of the group.
        If found, it returns the LanguageFamily object. If not found, it
        instead returns the string 'English or Unspecified'.
        """
        # Exception for Spanish language to keep the Indo-European languages
        # otherwise part of a single, continuous range while allowing Spanish
        # to be evaluated separately.
        if language_id == 1200:
            return LanguageFamily('Spanish', 1200, 1200)
        # Iterates through the family group until it can either successfully
        # classify the input or has tried all options.
        for entry in self._families:
            if self._families[entry].equals(language_id):
                return self._families[entry]
        return 'English or Unspecified'

    def __repr__(self):
        return str(self._families)
