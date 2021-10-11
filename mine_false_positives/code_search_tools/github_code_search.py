import time
from github import Github
import datetime

from fp_utils.github import wait
from code_search_tools.generic import remove_non_ascii


def file_info_2_line(file, code_keys, counter):
    info = [counter]
    for attr in code_keys:

        if attr is 'repository':
            attr_info = file.__getattribute__(attr).full_name
        else:
            attr_info = file.__getattribute__(attr)

        if attr_info is None:
            info.append('')
        else:
            info.append(str(attr_info).replace(',', '/'))

    line = ','.join(map(str, info))
    line += '\n'
    return line


def get_sizes(size_begin, step_size, times):
    sizes_list = []
    for x in range(0, times):
        size_end = size_begin + step_size
        sizes_list.append(f'size:{size_begin}..{size_end}')
        size_begin += step_size
    return sizes_list


class GithubCodeSearchByYear:
    def __init__(self, u, p, word, lang, years, github_search_result, code_keys):
        self.u = u
        self.p = p
        self.g = Github(u, p)
        self.word = word
        self.lang = lang
        self.years = years
        self.github_search_result = github_search_result
        self.code_keys = code_keys

        self.counter = 0

    def _search_code(self, year: int) -> list:
        """
        Search for files with NOSONAR in the given year.
        Return list of files.

        Seems to be useless, but it looks like this to save search rate.
        :param year: str, year
        """
        wait(self.g)
        result = []
        size = ['size:<=10000', 'size:10000..15000', 'size:>15000']
        for s in size:
            partial_query = f'{self.word} language:{self.lang} created:{year} {s}'
            print(partial_query)
            wait(self.g)
            result.append(self.g.search_code(partial_query))
        return result

    def run_github_search(self):
        """
        Main method to collect the files which contain {word} word.
        """

        for y in self.years:
            print(f'\nSearching in the year {y}.')
            for pages in self._search_code(y):
                for file in pages:
                    save_file = open(self.github_search_result, 'a')
                    save_file.write(remove_non_ascii(self._get_file_info(file)))
                    save_file.close()
                    self.counter += 1
            print(f'\nYear {y} finished.')

    def _get_file_info(self, file) -> str:
        """
        Creates a string from file information.

        :param file: github.ContentFile.ContentFile
        :return: str, concatenated list of information.
        """
        wait(self.g)
        return file_info_2_line(file, self.code_keys, self.counter)


class GithubCodeSearchBySize:
    def __init__(self, u, p, word, lang, github_search_result, code_keys):
        self.u = u
        self.p = p
        self.g = self.init_g()
        self.word = word
        self.lang = lang
        self.github_search_result = github_search_result
        self.code_keys = code_keys
        self.counter = 0

    def init_g(self):
        return Github(self.u, self.p, timeout=120)

    def _get_file_info(self, file) -> str:
        """
        Creates a string from file information.

        :param file: github.ContentFile.ContentFile
        :return: str, concatenated list of information.
        """
        wait(self.g)
        return file_info_2_line(file, self.code_keys, self.counter)

    def _search_code(self, size: str):
        """
        Search for files with NOSONAR in the given year.
        Return list of files.

        Seems to be useless, but it looks like this to save search rate.
        :param size: str, size of the file in bytes
        :return: paginated list
        """
        wait(self.g)
        query = f'{self.word} language:{self.lang} {size}'
        print('Query: ', query)

        query_ok = False
        result = ''
        exception_counter = 0
        while not query_ok:
            try:
                result = self.g.search_code(query)
                query_ok = True
            except Exception as e:
                exception_counter += 1
                print(e, 'will sleep for a min')
                if exception_counter > 3:
                    print('Continuous triggering. Sleep for 10 min.')
                    time.sleep(600)
                else:
                    print('Exception caught. Sleep for 1 min.')
                    time.sleep(60)
                query_ok = False

        if result == '':
            print('Something is wrong with the result.')

        return result

    @staticmethod
    def _get_js_sizes() -> list:
        """
        Manually created list.
        :return: list of sizes
        """
        sizes = ['size:>5000', 'size:1000..5000', 'size:500..1000', 'size:0..500']
        return sizes

    @staticmethod
    def _get_java_sizes() -> list:
        """
        Manually created list. To "minimize" cost of search code.
        :return: list of sizes
        """
        part0 = ['size:0..500']
        part1 = get_sizes(500, 100, 50)
        part2 = get_sizes(5500, 250, 18)
        part3 = ['size:10000..10250', 'size:10250..10500', 'size:10500..10550',
                 'size:10550..10580', 'size:10580..10590', 'size:10590..10593',
                 'size:10593..10595', 'size:10595..10600', 'size:10600..10750']
        part4 = get_sizes(10750, 250, 17)
        part5 = get_sizes(15000, 1000, 5)
        part6 = get_sizes(20000, 2000, 4)
        part7 = ['size:40000..50000', 'size:50000..60000', 'size:>=60000']

        return part0 + part1 + part2 + part3 + part4 + part5 + part6 + part7

    def get_sizes(self) -> list:
        """
        Get the default list of sizes.
        :return: list, list of sizes
        """
        if self.lang == 'javascript':
            return self._get_js_sizes()
        elif self.lang == 'java':
            return self._get_java_sizes()
        else:
            raise Exception('Neither java nor javascript!')

    def run_github_search(self, file_sizes, chunk_size=3, sleep_duration=10):
        """
        Main method to collect the files which contain {word} word.
        :param file_sizes: list, list of sizes
        :param chunk_size: int, default 3
        :param sleep_duration: int, default 10, sleep duration between chunks
        """
        start = datetime.datetime.now()
        n = chunk_size
        for i in range(0, len(file_sizes), n):

            chunk = file_sizes[i:i + n]
            print('Searching chunk: ', chunk)

            for s in chunk:
                print(f'\nSearching, size: {s}.')
                time.sleep(0.72)
                for code in self._search_code(s):
                    time.sleep(0.72)
                    wait(self.g)
                    save_file = open(self.github_search_result, 'a')
                    save_file.write(remove_non_ascii(self._get_file_info(code)))
                    save_file.close()
                    self.counter += 1
                print(f'\nSize: {s} finished.')
            print(f'\nChunk: {chunk} finished. Sleeping and reinitializing github object.')
            self.g = self.init_g()
            time.sleep(sleep_duration)
        end = datetime.datetime.now()
        print('Finished: ', end)
        print('Duration: ', end-start)
