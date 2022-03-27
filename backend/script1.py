import os
import shutil

import requests

# def deploy():
#     path1 = "D://Documentos//Mati//pruebatecnica//frontend//dist"  # compiled dist folder
#     path2 = "C://nginx-1.21.6//projects//pruebatecnica//dist"  # nginx project folder

#     value_1 = os.path.isdir(path1)
#     if not value_1:
#         return "\ndist folder not found at pruebatecnica/frontend\n"

#     value_2 = os.path.isdir(path2)
#     if value_2:
#         mydir = path2
#         try:
#             shutil.rmtree(mydir)
#             shutil.move(path1, path2)
#             print("\nDone\n")
#         except OSError as e:
#             print("Error: %s - %s." % (e.filename, e.strerror))
#     else:
#         try:
#             result = shutil.move(path1, path2)
#             print("\nDone\n")
#         except Exception as e:
#             print(e)


def write_info(path, text):
    with open(path, 'a') as f:
        f.write(text)


def get_api_json():
    base_url = "http://localhost:5001"
    full_url = base_url + "/openapi.json"

    payload = {}
    headers = {}

    response = requests.request("GET", full_url, headers=headers, data=payload)

    if response.status_code == 200:
        if not os.path.exists("postman"):
            os.mkdir("postman")
        else:
            shutil.rmtree("postman")
            os.mkdir("postman")

        write_info('postman/openapi.json', response.text)

        postman_text = """How to import API documentation into Postman

        1) Open Postman
        2) Go to "APIs", select "Create an API", select "Import" tab
        3) Under "Import local schema files", hit "Select files" Button
        4) Select openapi.json located inside postman directory
        5) On next page, click on Import button and then on Close button
        6) API docs is imported on Collections and APIs Tabs. Use what you like
        7) Go to FastAPIDocumentation > draft > FastAPIDocumentation > Variables
        8) Set baseUrl:
            VARIABLE: baseUrl
            INITIAL VALUE: /
            CURRENT VALUE: """ + base_url + """
            Be sure this field is checked
        9) Click on Save Button (upper right located)
        10) Now, you can test every endpoint
            Example: {{baseUrl}}/logs
        
        """

        write_info('postman/README.md', postman_text)

        return "\nAPI docs copied to postman/openapi.json and README.md created\n"
    else:
        return "\nStatus code: " + str(response.status_code) + "\n"


if __name__ == "__main__":
    # print(deploy())
    print(get_api_json())
