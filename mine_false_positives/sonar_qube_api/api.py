import requests
import json


class SonarQube:

    def __init__(self, token, port):
        self.token = token
        self.port = port

    def _create_session(self):
        """
        Create and return a session obj.
        :return: requests.Session
        """
        session = requests.Session()
        session.auth = self.token, ''
        return session

    def _response(self, url, info_string, method='get'):
        """
        Can handle post or get requests.

        :param url: str
        :param info_string: str, arbitrary e.g. the component_key, debugging purpose.
        :param method:str, can be `get` or `post`
        :return: None if error occurred else response in json format.
        """
        sess = self._create_session()
        response = None
        try:
            result = sess.__getattribute__(method)(url)
            binary = result.content
            response = json.loads(binary)
            if response is '':
                print(f'Empty response -> {info_string}')
        except Exception as e:
            print(f'Error occurred: {e}')
            return response
        return response

    @staticmethod
    def _get_kwargs_parameters(kwargs):
        """
        Make a concatenated url parameters string from keyword arguments.

        :param kwargs: dict, intended to be generic **kwargs passed to functions
        :return:
        """
        if kwargs == {}:
            parameters = ""
        else:
            parameters = "?"
            for key in kwargs:
                parameters += f'{key}={kwargs[key]}&'
            # to skip the last &
            parameters = parameters[:-1]
        return parameters

    def api_issues_search(self, verbose=False, p=1, ps=500, **kwargs):
        """
        Search issues in projects. Main use is to give 'componentKeys' e.g. project_key:file_name and/or a specific
        `rule` and get the related issues on that file.

        available keys:
        - additionalFields
            optional
            Comma-separated list of the optional fields to be returned in response.
            Action plans are dropped in 5.5, it is not returned in the response.
            Possible values: _all, comments, languages, actionPlans, rules, transitions, actions, users
        - asc
            optional
            Ascending sort.
            Possible values: true, false, yes, no, Default value:true
        - assigned
            optional
            To retrieve assigned or unassigned issues.
            Possible values: true, false, yes, no
        - assignees
            optional
            Comma-separated list of assignee logins. The value '__me__' can be used as a placeholder
            for user who performs the request.
            Example value: admin, usera, __me__
        - authors
            optional
            Comma-separated list of SCM accounts.
            Example value: torvalds@linux-foundation.org
        - componentKeys
            optional
            Comma-separated list of component keys. Retrieve issues associated to a specific list of components
            (and all its descendants). A component can be a portfolio, project, module, directory or file.
            Example value: my_project
        - createdAfter
            optional
            To retrieve issues created after the given date (inclusive). Either a date (server timezone) or datetime
            can be provided.If this parameter is set, createdSince must not be set.
            Example value: 2017-10-19 or 2017-10-19T13:00:00+0200
        - createdAt
            optional
            Datetime to retrieve issues created during a specific analysis.
            Example value: 2017-10-19T13:00:00+0200
        - createdBefore
            optional
            To retrieve issues created before the given date (inclusive).
            Either a date (server timezone) or datetime can be provided.
            Example value: 2017-10-19 or 2017-10-19T13:00:00+0200
        - createdInLast
            optional
            To retrieve issues created during a time span before the current time (exclusive).
            Accepted units are 'y' for year, 'm' for month, 'w' for week and 'd' for day.
            If this parameter is set, createdAfter must not be set.
            Example value: 1m2w (1 month 2 weeks)
        - cwe
            optional
            Comma-separated list of CWE identifiers. Use 'unknown' to select issues not associated to any CWE.
            Example value: 12, 125, unknown
        - facetMode
            optional
            Choose the returned value for facet items, either count of issues or sum of debt.
            Since 5.5, 'debt' mode is deprecated and replaced by 'effort'
            Possible values: count, effort, debt, Default value: count
        - facets
            optional
            Comma-separated list of the facets to be computed. No facet is computed by default.
            Since 5.5, facet 'actionPlans' is deprecated.
            Since 5.5, facet 'reporters' is deprecated.
            Possible values: severities, statuses, resolutions, actionPlans, projectUuids,
                rules, assignees, assigned_to_me, reporters, authors, moduleUuids, fileUuids,
                directories, languages, tags, types, owaspTop10, sansTop25, cwe, createdAt
        - issues
            optional
            Comma-separated list of issue keys
            Example value: 5bccd6e8-f525-43a2-8d76-fcb13dde79ef
        - languages
            optional
            Comma-separated list of languages. Available since 4.4
            Example value: java,js
        - onComponentOnly
            optional
            Return only issues at a component's level, not on its descendants (modules, directories, files, etc).
            This parameter is only considered when componentKeys or componentUuids is set.
            Using the deprecated componentRoots or componentRootUuids parameters will set this parameter to false.
            Using the deprecated components parameter will set this parameter to true.
            Possible values: true, false, yes, no, Default value: false
        - owaspTop10
            optional
            since 7.3
            Comma-separated list of OWASP Top 10 lowercase categories.
            Use 'unknown' to select issues not associated to any OWASP Top 10 category.
            Possible values: a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, unknown
        - p
            optional
            1-based page number
            Default value: 1
            Example value: 42
        - ps
            optional
            Page size. Must be greater than 0 and less or equal than 500
            Default value: 100
            Example value: 20
        - resolutions
            optional
            Comma-separated list of resolutions
            Possible values: FALSE-POSITIVE, WONTFIX, FIXED, REMOVED
            Example value: FIXED, REMOVED
        - resolved
            optional
            To match resolved or unresolved issues
            Possible values: true, false, yes, no
        - rules
            optional
            Comma-separated list of coding rule keys. Format is <repository>:<rule>
            Example value: squid:AvoidCycles
        - s
            optional
            Sort field
            Possible values: CREATION_DATE, UPDATE_DATE, CLOSE_DATE, ASSIGNEE, SEVERITY, STATUS, FILE_LINE
        - sansTop25
            optional
            since 7.3
            Comma-separated list of SANS Top 25 categories.
            Possible values: insecure-interaction, risky-resource, porous-defenses
        - severities
            optional
            Comma-separated list of severities
            Possible values: INFO, MINOR, MAJOR, CRITICAL, BLOCKER
            Example value: BLOCKER, CRITICAL
        - sinceLeakPeriod
            optional
            To retrieve issues created since the leak period.
            If this parameter is set to a truthy value,
            createdAfter must not be set and one component id or key must be provided.
            Possible values: true, false, yes, no, Default value: false
        - statuses
            optional
            Comma-separated list of statuses
            Possible values: OPEN, CONFIRMED, REOPENED, RESOLVED, CLOSED
            Example value: OPEN, REOPENED
        - tags
            optional
            Comma-separated list of tags.
            Example value: security, convention
        - types
            optional
            since 5.5
            Comma-separated list of types.
            Possible values: CODE_SMELL, BUG, VULNERABILITY, SECURITY_HOTSPOT
            Default value: BUG, VULNERABILITY, CODE_SMELL
            Example value: CODE_SMELL, BUG

        :param verbose: bool, print out the url or not
        :param p: int, start at the given page
        :param ps: int, page size
        :return: None if error else json
        """
        kwargs['p'] = p
        kwargs['ps'] = ps
        parameters = self._get_kwargs_parameters(kwargs)
        url = f'http://localhost:{self.port}/api/issues/search{parameters}'
        if verbose:
            print(url)
        return self._response(url, 'get')

    def api_projects_bulk_delete(self, **kwargs):
        """
        Intended to be used to delete multiple projects at once. E.g. Select all projects, that contain `nosonar` in
        project name, q=nosonar, and delete tham

        parameters:
        - analyzedBefore
            optional
            since 6.6
            Filter the projects for which last analysis is older than the given date (exclusive).
            Either a date (server timezone) or datetime can be provided.
            Example value: 2017-10-19 or 2017-10-19T13:00:00+0200
        - onProvisionedOnly
            optional
            since 6.6
            Filter the projects that are provisioned
            Possible values: true, false, yes, no
            Default value: false
        - projects:
            optional
            Comma-separated list of project keys
            Example value: my_project, another_project
        - q:
            optional
            Limit to:
            component names that contain the supplied string
            component keys that contain the supplied string
            Example value: sonar
        - qualifiers
            optional
            Comma-separated list of component qualifiers. Filter the results with the specified qualifiers
            Possible values: TRK, VW, APP
            Default value:TRK

        :return: return None if error else json
        """
        parameters = self._get_kwargs_parameters(kwargs)
        url = f'http://localhost:{self.port}/api/projects/bulk_delete{parameters}'
        return self._response(url, parameters, 'post')
