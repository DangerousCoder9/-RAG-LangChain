#   → Access environment variables, file paths, system ops.
import os
#   → Make HTTP requests (call APIs, fetch data).
import requests
#   → Load variables from a `.env` file into environment (e.g., API keys).
from dotenv import load_dotenv
#   → Use `Document` class to structure text data (content + metadata) for LangChain.
from langchain_core.documents import Document

# writing a load.env function to search for the present of a .env file and load all the enviornmenet variables (API KEYS) for us 
load_dotenv()

# now lets store the github token in a var 
github_token = os.getenv("GITHUB_TOKEN")

# Fetches the folder and file structure of a GitHub repository.
'''
**Example:**

```python
owner = "octocat"
repo = "Hello-World"
endpoint = "issues"

issues = fetch_github(owner, repo, endpoint)
print(issues)
```

**What happens inside your function:**

* Builds URL →
  `https://api.github.com/repos/octocat/Hello-World/issues`
* Sends GET request with your token
* Gets response → list of issues

**Returned value (`issues`):**

```json
[
  {
    "title": "Bug in login",
    "body": "App crashes",
    "user": {"login": "john123"},
    "comments": 2,
    "labels": [],
    "created_at": "2024-01-01T10:00:00Z"
  }
]
```
**Use:**
This `issues` list is directly passed into `load_issues(issues)`.
'''
def fetch_github(owner, repo, endpoint):

    # owner → GitHub username/org
    # repo → repository name
    # endpoint → API path (e.g., "contents", "contents/src")

    # Build full GitHub API URL dynamically
    # Example: https://api.github.com/repos/user/repo/contents
    url = f"https://api.github.com/repos/{owner}/{repo}/{endpoint}"
   # Create HTTP headers for the API request
    headers = {
        # Authorization header sends your GitHub token
        # Used to authenticate requests (avoid rate limits, access private repos)
        "Authorization": f"token {github_token}",
    }

    # Send an HTTP GET request to the GitHub API
    # url → API endpoint we built earlier
    # headers → includes Authorization token for authentication
    response = requests.get(url, headers=headers)
    # response now contains:
    # - status_code → success/failure (e.g., 200 OK)
    # - data → can be accessed via response.json()

    if response.status_code == 200:
        # If successful, return the JSON data (folder/file structure)
        return response.json() # this will be a dictionary or list of files/folders
    else:
        # If not successful, print error and return None
        print(f"Failed to fetch data: {response.status_code}")
        return None

# This will take all the issues we get from the fetch_github and parse them and load them in document in langchain so that we can use them as RAG
'''
**Direct answer:**
It takes GitHub issues and turns each one into a clean “document” with text + details.

**Step-by-step (simple):**

* For each issue:

  * Take **title + body → main text**
  * Collect extra info → author, comments, labels, date
* Create a `Document` object:

  * `page_content` = text
  * `metadata` = extra info
* Store all documents in a list

**Example:**

* Title: “Bug in login”
* Body: “App crashes”
  → Text = `"Bug in loginApp crashes"`

**Result:**
A list of documents you can easily search or use in AI models.
output :
Document(
    page_content='Bug in login\nApp crashes',
    metadata={
        'author': 'john123',
        'comments': 2,
        'body': 'App crashes',
        'labels': [],
        'created_at': '2024-01-01T10:00:00Z'
    }
)
'''
def load_issues(issues):
    docs = []  # list to store all Document objects

    # loop through each issue in the input list
    for entry in issues:
        
        # collect useful extra information (metadata)
        metadata = {
            "author": entry["user"]["login"],      # username of issue creator
            "comments": entry["comments"],         # number of comments
            "body": entry["body"],                 # issue description
            "labels": entry["labels"],             # issue labels/tags
            "created_at": entry["created_at"]      # issue creation date
        }

        # start main text with the issue title
        data = entry["title"]

        # if body exists, append it to the title
        if entry["body"]:
            data = data + entry["body"]

        # create a Document object with text + metadata
        doc = Document(page_content=data, metadata=metadata)

        # add this document to the list
        docs.append(doc)

    # return the final list of documents
    return docs

'''
Document(
    page_content='Bug in login\nApp crashes',
    metadata={
        'author': 'john123',
        'comments': 2,
        'body': 'App crashes',
        'labels': [],
        'created_at': '2024-01-01T10:00:00Z'
    }
)
'''
def fetch_github_issues(owner , repo):
    data = fetch_github(owner, repo, "issues")
    return load_issues(data) 

# calling the fetch githtub function 
owner = "techwithtim"
repo = "Flask-Web-App-Tutorial"
endpoint = "issues"
data = fetch_github(owner, repo, endpoint)
print(data)