all_java_repos_stars_gt1 = '''
{
  rateLimit{
    cost
    limit
    remaining
  }
  search(query:"language:java stars:>0", type: REPOSITORY, first:1){
    codeCount
  }
}
'''
repository_by_year = '''
{{
  rateLimit{{
    cost
    limit
    remaining
  }}
  search(query:"language:java created:{0} stars:>0", type: REPOSITORY, first:100{1}){{
    codeCount
    pageInfo{{
      hasNextPage
      endCursor
    }}
    edges{{
      node{{
        ... on Repository{{
          nameWithOwner
          sshUrl
        }}
      }}
    }}
  }}
}}
'''

commits_in_repo ='''
query {{
  rateLimit{{
    cost
    limit
    remaining
  }}
  repository(owner:"{0}",  name:"{1}"){{
    pullRequests(first:100{2}){{
      totalCount
      pageInfo{{
        endCursor
        hasNextPage
      }}

      edges{{
        node{{
          title
          commits(first:100{3}){{
            totalCount
            pageInfo{{
              endCursor
              hasNextPage
            }}

            edges{{
              node{{
                commit{{
                  id
                  message
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
'''

sonar_word_in_pr_by_date = '''
{{
  rateLimit{{
    remaining
    cost
  }}
  search(type:ISSUE, query:"is:pr sonar language:java created:{0}", first:100{1}){{
    codeCount
    pageInfo{{
      hasNextPage
      endCursor
    }}
    edges{{
      node{{
        ... on PullRequest{{
          id
        }}
      }}
    }}
  }}
}}'''

gather_sonar_word_pr_by_date = '''
{{
  rateLimit{{
    remaining
    cost
  }}
  search(type:ISSUE, query:"is:pr sonar language:java created:{0}", first:100{1}){{
    codeCount
    pageInfo{{
      hasNextPage
      endCursor
    }}
    edges{{
      node{{
      __typename
        ... on PullRequest{{
          id
          bodyText
        }}
      }}
    }}
  }}
}}'''

gather_specific_word_pr_by_date = '''
{{
  rateLimit{{
    remaining
    cost
  }}
  search(type:ISSUE, query:"is:pr {0} language:{1} created:{2}", first:100{3}){{
    codeCount
    pageInfo{{
      hasNextPage
      endCursor
    }}
    edges{{
      node{{
      __typename
        ... on PullRequest{{
          id
          bodyText
          title
          comments(first:100){{
            edges{{
              node{{
                ... on IssueComment{{
                  bodyText
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}'''

get_codeCount_of_month = '''
{{
  rateLimit{{
    remaining
    cost
  }}
  search(type:ISSUE, query:"is:pr {0} language:{1} created:{2}", first:1){{
    codeCount
  }}
}}
'''


query_repo_stats = '''
{{
  rateLimit{{
    remaining
  }}
  repository(owner:"{0}", name:"{1}"){{
    stargazers(first:1){{
    totalCount
    }}
    forkCount
    isDisabled
    isLocked
    isPrivate
    isMirror
    viewerCanAdminister
        watchers(first:1){{
      totalCount
    }}
  }}
}}
'''


#    baseRef{{
#      name
#      id
#    }}