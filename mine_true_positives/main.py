from gather import TruePositiveSquidSearcher
from sonar_tools import MultiSonarScanner
from tp_utils.keys import KeyHolder
from sonar_tools.scan_projects import ProjectScanner


u = "github user"
p = "github password "
github_token = 'github token'
sonar_token = 'sonar token'

date = {
        'start_year': 2010,
        'end_year': 2020,
        'start_month': 1,
        'end_month': 12
}
word = 'sonar'
patterns = [r'(squid:s\d+)', r'(squid:\w+)', r'(squid%3aS\d+)',
            r'(squid%3A\w+)']

tpss = TruePositiveSquidSearcher(u, p, github_token, date, word, patterns, datetimedate=(2020, 8, 27))
tpss.gather_pull_requests()
tpss.filter_pull_requests()
tpss.gather_commits_from_pr()
tpss.filter_commits()
tpss.gather_files()
print(tpss.file_keys)
print(tpss.csv_result_keys)
tpss.search_sonar_locations()

tpss.check_java_files()
tpss.load_good_files_list()
tpss.create_project_names_and_good_files_chunks(project_base='0827', size=10000)

print(tpss.projects_and_chunks)

ms = MultiSonarScanner(token=sonar_token,
                       projects_and_chunks=tpss.projects_and_chunks,
                       lang=tpss.lang,
                       good_files_csv=tpss.good_files_csv,
                       log_file=tpss.log_txt)
ms.bulk_sonar_scan()

keys = KeyHolder()

projects = {k + '_Key': v for k, v in tpss.projects_and_chunks.items()}
ps = ProjectScanner(token=sonar_token,
                    projects_and_chunks=projects,  #tpss.projects_and_chunks,
                    patch_checked_csv=tpss.patch_checked_csv,
                    patch_located_keys=keys.get_patched_keys(),
                    result_keys=keys.get_project_scan_res_keys(),
                    good_files_csv_path=tpss.good_files_csv,
                    result_folder=tpss.squid_folder,
                    result_file_base_name='0827_java')
ps.search_projects_issues()

######################################################################
# JS example:
# date = {
#         'start_year': 2010,
#         'end_year': 2020,
#         'start_month': 1,
#         'end_month': 12
# }
# word = 'sonar'
#
# basic_patterns = [r'(squid:s\d+)', r'(squid:\w+)', r'(squid%3aS\d+)',
#                   r'(squid%3A\w+)']
#
# javascript_patterns = [r'(javascript:s\d+)', r'(javascript:\w+)', r'(javascript%3aS\d+)',
#                        r'(javascript%3A\w+)']
#
# patterns = basic_patterns + javascript_patterns
#
# tpss = TruePositiveSquidSearcher(user=u,
#                                  password=p,
#                                  token=github_token,
#                                  date_ops=date,
#                                  searched_word=word,
#                                  filtering_patterns=patterns,
#                                  lang='javascript',
#                                  file_type='.js',
#                                  datetimedate=(2020, 3, 4))
# tpss.gather_pull_requests()
# tpss.filter_pull_requests()
# tpss.gather_commits_from_pr()
# tpss.filter_commits()
# tpss.gather_files()
# tpss.search_sonar_locations()
