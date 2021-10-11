from sonar_tools import ProjectScanner
from sonar_tools import MultiSonarScanner
from code_search_tools import GatherNosonarFiles


user="github_user"
password = "github_password"
sonar_token = "token"

gnf = GatherNosonarFiles(user, password, 'NOSONAR', run_time=(2020, 1, 26), lang='java')

# PART 1 - Get the files
gnf.code_size_search()
gnf.download_files()
gnf.modify_files()
gnf.check_java_files()

# PART 2 - Sonar scanning
gnf.load_good_files_list()
base_name = 'project_1_26_'
projects = gnf.create_project_names_and_good_files_chunks(project_base=base_name, size=2000)
multi_ss = MultiSonarScanner(token=sonar_token,
                             projects_and_chunks=projects,
                             lang=gnf.lang,
                             good_files_csv=gnf.good_files_csv)
project_keys = multi_ss.bulk_sonar_scan()

# In case of failure
# Look at the log file. Search for project and if needed find the troublesome file.
# Get the borders = projects['project_1_26__chunk_23']
# Get a concatenated list of files print(','.join(gnf.good_files_list[borders[0]: borders[1]]))
# manually copy to properties file. Don't forget to change the project name and key.
# skip the unwanted file
# cmd > sonar scan
# or
# failed_project = 'project_1_26__chunk_23'
# borders = projects['project_1_26__chunk_23']
# ss = SonarScanner(sonar_token, failed_project, lang=gnf.lang, files_list=gnf.good_files_list[borders[0]: borders[1]])
# ss.run_scan()


# project_keys should come from multi sonar scanner run, but if not:
project_keys = {k+'_Key': v for k, v in projects.items()}
ps = ProjectScanner(token=sonar_token,
                    projects_and_chunks=project_keys,
                    modified_csv_path=gnf.modification_csv,
                    modified_csv_keys=gnf.modified_keys,
                    good_files_csv_path=gnf.good_files_csv,
                    result_folder=gnf.squid_folder,
                    result_file_base_name=base_name)
ps.search_projects_issues()
