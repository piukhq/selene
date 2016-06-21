
class CSVReader(object):

    def __init__(self, column_names, delimiter, keep=None):
        # names should not have duplicates
        if len(set(column_names)) != len(column_names):
            raise ValueError('name array cannot contain duplicates')
        self._column_names = column_names
        if keep is None:
            keep = {x: None for x in column_names}
        self._keep = keep
        self._delimiter = delimiter
        self._count = 0

    def __iter__(self):
        return self

    def __next__(self):
        line = self._file.readline().strip()
        if line:
            self._count += 1
            entry = {}
            columns = [x.strip() for x in line.split(self._delimiter)]
            if len(columns) < len(self._column_names):
                raise ValueError('fault csv line {0} found in {1}'.format(self._file_name, self._count))
            for name, value in zip(self._column_names, columns):
                if name in self._keep:
                    entry[name] = value
            return entry
        else:
            self._file.close()
            raise StopIteration()

    def __call__(self, filename):
        self._file = open(filename)
        self._file_name = filename
        return self


class CSVWriter(object):

    def __init__(self, filename, column_names, write_header=True):
        import csv
        self._file = open(filename, 'w')
        self._writer = csv.DictWriter(self._file, fieldnames=column_names)
        self._column_names = column_names
        if write_header:
            self._writer.writeheader()

    def write_data(self, data):
        for item in data:
            self._writer.writerow(item)

    def __del__(self):
        self._file.close()
