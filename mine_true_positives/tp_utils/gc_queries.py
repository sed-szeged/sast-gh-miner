commit_gatherer_from_pr_node_query = '''
query{{
  rateLimit{{
    remaining
  }}
    node(id:"{0}"){{
  ... on PullRequest{{
    commits(first:100{1}){{
    totalCount
    pageInfo{{
    hasNextPage
    endCursor
    }}
      edges{{
        node{{
          commit{{
            message
            repository{{
              nameWithOwner
            }}
            id
            oid
          }}
        }}
      }}
    }}
  }}
}}
}}
'''