import requests

BASE_URL = "https://tamdentist.tdental.vn"
USERNAME = "dataconnect"
PASSWORD = "dataconnect@"

def get_total_customers():
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/Account/Login", json={
        "userName": USERNAME,
        "password": PASSWORD,
        "rememberMe": False
    })
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    r = session.get(f"{BASE_URL}/api/Partners/GetPagedPartnersCustomer", params={"offset": 0, "limit": 1}, headers=headers)
    data = r.json()
    return data.get("totalItems")

if __name__ == "__main__":
    try:
        total = get_total_customers()
        print(f"Total Customers: {total}")
    except Exception as e:
        print(f"Error: {e}")
