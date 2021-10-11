# def do_twice(func):
#
#     def wrapper_do_twice(*args, **kwargs):
#         start = datetime.datetime.now()
#         self._save_log(str_date(start))
#         func(*args, **kwargs)
#         func(*args, **kwargs)
#     return wrapper_do_twice
#
# print('Gathering pull requests...')
#
#
#         gpr = GatherPullRequests(github_token=self.github_token,
#                                  date_ops=self.date_ops,
#                                  specific_word=self.searched_word,
#                                  pull_request_csv=self.pr_csv,
#                                  keys=self.pr_keys,
#                                  sec=self.sec,
#                                  lang=self.lang)
#         stat = gpr.execute(reset)
#         end = datetime.datetime.now()
#         self._save_log(str_date(end))
#         self._save_log(str_date(end - start))
#         self._save_log_gpr(stat)
#         print(f'Start time: {start}\nEnd time: {end}')
#         print(f'Duration time: {end - start}')
#         print('Pull request gathering is finished.\n')
#         print('Done')