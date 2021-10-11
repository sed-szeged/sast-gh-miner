from code_search_tools import GatherNosonarFiles
from sonar_tools import ProjectScanner, MultiSonarScanner, SonarScanner

user="github_user"
password = "github_password"
sonar_token = "token"


######################################################################
# End to end example:
# gathering .java files with NOSONAR
######################################################################
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 8, 1), lang='java')
sizes = ['size:200..500']
gnf.code_size_search(file_sizes=sizes)
gnf.download_files()
gnf.modify_files()
gnf.check_java_files()
gnf.create_project_names_and_good_files_chunks(project_base='august')

print(gnf.projects_and_chunks)
print(gnf.good_files_csv)
ms = MultiSonarScanner(token=sonar_token, projects_and_chunks=gnf.projects_and_chunks,
                       lang=gnf.lang, good_files_csv=gnf.good_files_csv)
projects = ms.bulk_sonar_scan()
print(projects)

ps = ProjectScanner(token=sonar_token,
                    projects_and_chunks=gnf.projects_and_chunks,
                    modified_csv_path=gnf.modification_csv,
                    modified_csv_keys=gnf.modified_keys,
                    good_files_csv_path=gnf.good_files_csv,
                    result_folder=gnf.squid_folder,
                    result_file_base_name='proba_8_5_')
ps.search_projects_issues()



######################################################################
# File collecting example:
# gathering .js files with NOSONAR
######################################################################
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 8, 6), lang='javascript')
gnf.code_size_search()  # with predefined sizes
gnf.download_files()


######################################################################
# Sonar Scanner related examples:
# First take a look at projects and chunks
# at this point good_files -csv that contains the files without parsing or similar errors- already should be created.
######################################################################
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 1, 10), lang='java')
gnf.load_good_files_list()
for k, v in gnf.create_project_names_and_good_files_chunks().items():
    print(k, v)

# USE CASE 1:
# scan all the projects in project_and_chunks
# already created good_files, separate session from files gathering.
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 1, 10), lang='java')
gnf.load_good_files_list()
multi_ss = MultiSonarScanner(token=sonar_token,
                             projects_and_chunks=gnf.create_project_names_and_good_files_chunks(),
                             lang='java',
                             good_files_csv='results/2020_1_10_NOSONAR_java/csv/good_files.csv')
multi_ss.bulk_sonar_scan()

# USE CASE 2:
# specify a project base name
project_base_name = 'qp_all_1_21_'
lang = 'java'
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 1, 10), lang=lang)
gnf.load_good_files_list()
projects_and_chunks = gnf.create_project_names_and_good_files_chunks(project_base=project_base_name)
multi_ss = MultiSonarScanner(token=sonar_token,
                             projects_and_chunks=projects_and_chunks,
                             lang=lang,
                             good_files_csv='results/2020_1_10_NOSONAR_java/csv/good_files.csv')
multi_ss.bulk_sonar_scan()


# USE CASE 3:
# Scanning a single project.
borders = [9000, 10000]
lang = 'java'
project_name = 'qp_all_1_21_chunk_10'
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 1, 10), lang=lang)
gnf.load_good_files_list()
chunk = gnf.good_files_list[borders[0]:borders[1]]
single_ss = SonarScanner(token=sonar_token,
                         project_name=project_name,
                         lang=lang,
                         files_list=chunk)
single_ss.run_scan()

# USE CASE 4:
# For manual sonar-scanner get the failed project and the files.
gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 1, 10), lang='java')
gnf.load_good_files_list()
projects = gnf.create_project_names_and_good_files_chunks()
# select the failed project:
borders = projects['failed']
print(','.join(map(str, gnf.good_files_list[borders[0], borders[1]])))
