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
