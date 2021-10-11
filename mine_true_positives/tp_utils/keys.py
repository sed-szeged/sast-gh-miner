class KeyHolder:
    def __init__(self):

        self._pull_request_keys = ['id', 'pid', 'txt']
        self._commit_keys = ['id', 'pid', 'c_id', 'c_oid', 'c_repo', 'pr_squids', 'c_msg']
        self._commit_filtered_keys = ['id', 'pid', 'c_id', 'c_oid', 'repo', 'possible_squids']

        self._file_keys = self._commit_filtered_keys + ['current_sha', 'prev_sha', 'current_url',
                                                        'prev_url', 'patch_location',
                                                        'prev_file_location', 'current_file_location']

        self._patch_locator_keys = self._file_keys + ['patch_start_row', 'patch_end_row']

        self._project_scan_res_keys = self._patch_locator_keys + ['startLine', 'endLine', 'startOffset',
                                                                  'endOffset', 'rule', 'severity', 'message']

    def get_pull_request_keys(self):
        return self._pull_request_keys

    def get_commit_keys(self):
        return self._commit_keys

    def get_commit_filtered_keys(self):
        return self._commit_filtered_keys

    def get_file_keys(self):
        return self._file_keys

    def get_patched_keys(self):
        return self._patch_locator_keys

    def get_project_scan_res_keys(self):
        return self._project_scan_res_keys
