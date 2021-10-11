class KeyHolder:
    def __init__(self):

        self._github_file_keys = ['name', 'sha', 'repository',
                                  'encoding', 'size', 'type',
                                  'path',
                                  'etag', 'last_modified', 'license',
                                  'url', 'download_url', 'git_url', 'html_url']

        self._code_search_keys = ['id'] + self._github_file_keys

        self._download_keys = self._code_search_keys + ['original_file_path']

        self._modified_keys = self._download_keys + ['modified_file', 'mods', 'flags']

        self._result_info_keys = self._modified_keys + ['modification', 'rule', 'severity', 'message',
                                                        'startLine', 'endLine', 'startOffset', 'endOffset']

    def get_github_file_keys(self):
        """
        Available data about a github file object.
        This is the base for upcoming keys.
        :return: list, github_file_keys
        """
        return self._github_file_keys

    def get_code_search_keys(self):
        """
        Should be used while the base info is retrieved from github code search.
        Also an uid is added to front as a counter.
        :return: list, code_search_keys
        """
        return self._code_search_keys

    def get_download_keys(self):
        """
        Should be used while downloading files.
        The downloaded file location is appended to the list.
        :return: list, download_keys
        """
        return self._download_keys

    def get_modified_keys(self):
        """
        Should be used while modifying files.
        The modified file location is appended to the list with
        - `mods` : the modified line numbers
        - `flags` : comments after //NOSONAR.
        :return: list, download_keys
        """
        return self._modified_keys

    def get_result_info_keys(self):
        """
        This is the last step.
        Should be used while scanning projects.
        Added information:
        - `modification` : actual modification line number
        - `rule`         : squid
        - `severity`     : squid severity according to SonarQube
        - `message`      : description of the rule
        - `startLine`    : squid starting line
        - `endLine`      : squid ending line
        - `startOffset`  : squid starting column
        - `endOffset`    : squid ending column
        :return: list, result_info_keys
        """
        return self._result_info_keys
