
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
