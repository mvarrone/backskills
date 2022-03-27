import os
import shutil

import requests


def write_info(path, text) -> None:
    with open(path, 'a') as f:
        f.write(text)


def create_json_file_for_api_docs(base_url) -> dict:
    full_url = base_url + "/openapi.json"

    payload = headers = {}

    try:
        response = requests.request(
            "GET", full_url, headers=headers, data=payload)
    except Exception as e:
        return {
            "error": True,
            "info": e.args,
            "status_code": 500
        }

    if response.status_code == 200:
        if not os.path.exists("postman"):
            os.mkdir("postman")
        else:
            shutil.rmtree("postman")
            os.mkdir("postman")

        write_info('postman/openapi.json', response.text)

        return {
            "info": "API docs created at postman/openapi.json",
            "status_code": response.status_code
        }
    return {
        "info": "Bad status code on response: " + str(response.status_code),
        "status_code": response.status_code
    }


def create_readme_file_for_postman(base_url) -> str:
    postman_text = """# How to import API documentation into Postman

1. Open Postman
2. Go to "APIs", select "New", inside "Advanced" section select "API" and then "Import" tab
3. Under "Import local schema files", hit "Select files" Button
4. Select openapi.json located inside postman directory
5. On next page, click on Import button and then on Close button
6. API docs is imported on Collections and APIs Tabs. Use what you like
7. Go to FastAPIDocumentation > draft > FastAPIDocumentation > Variables
8. Set baseUrl:
    - VARIABLE: baseUrl
    - INITIAL VALUE: /
    - CURRENT VALUE: """ + base_url + """
    - Be sure this field is checked
9. Click on Save Button (upper right located)
10. Now, you can test every endpoint

    Example: {{baseUrl}}/logs

"""
    write_info('postman/README.md', postman_text)
    return "README.md created at postman/README.md\n"


if __name__ == "__main__":
    base_url = "http://localhost:5001"
    response = create_json_file_for_api_docs(base_url)
    print("\n")
    print(response["info"], "\n")

    if response["status_code"] == 200:
        print(create_readme_file_for_postman(base_url))
