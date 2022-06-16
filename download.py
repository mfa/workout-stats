import json
from pathlib import Path

import click
import httpx


def get_new_refresh_token():
    fn = Path("_secrets.json")
    _secrets = json.load(fn.open())

    params = {
        "client_id": _secrets["client_id"],
        "response_type": "code",
        "redirect_uri": "http://localhost",
        "approval_prompt": "force",
        "scope": "read,activity:read_all",
    }
    r = httpx.Request(
        method="GET", url="https://www.strava.com/oauth/authorize", params=params
    )
    print("--> copy url in browser:")
    print(r.url)
    print()
    code = input("insert 'code' from url here: ")

    data = {
        "client_id": _secrets["client_id"],
        "client_secret": _secrets["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
    }
    response = httpx.post(url="https://www.strava.com/oauth/token", data=data)
    _secrets["refresh_token"] = response.json()["refresh_token"]
    json.dump(_secrets, fn.open("w"), indent=2)
    print("refresh_token was added to _secrets.json")
    return _secrets


def get_access_token():
    data = json.load(Path("_secrets.json").open())
    if "refresh_token" not in data:
        data = get_new_refresh_token()

    data.update({"grant_type": "refresh_token"})
    r = httpx.post(url="https://www.strava.com/api/v3/oauth/token", data=data)
    if r.status_code == 200:
        return r.json()["access_token"]


def update_data():
    access_token = get_access_token()

    activity_ids = []
    headers = {"Authorization": f"Bearer {access_token}"}

    # collect all "Rowings"
    page = 1
    while True:
        params = {"per_page": 100, "page": page}
        result = httpx.get(
            url="https://www.strava.com/api/v3/athlete/activities",
            params=params,
            headers=headers,
        )
        for item in result.json():
            if item.get("type") == "Workout" and "Rowing" in item.get("name"):
                activity_ids.append(item.get("id"))
                # write to rowing table:
                # id, start_data, name, start_date_local
            if item["start_date"].startswith("2019-11"):
                # my rowing begins in December 2019
                break
        else:
            click.echo(f"Last item {item['start_date']}")
            page += 1
            continue
        break

    activities = []
    # get all the details
    with click.progressbar(activity_ids) as bar:
        for item in bar:
            result = httpx.get(
                url=f"https://www.strava.com/api/v3/activities/{item}", headers=headers
            )
            d = {}
            result = result.json()
            for key in [
                "name",
                "moving_time",
                "start_date",
                "start_date_local",
                "description",
                "suffer_score",
                "has_heartrate",
                "average_heartrate",
                "max_heartrate",
            ]:
                d[key] = result.get(key)

            # get heartrate stream
            result = httpx.get(
                url=f"https://www.strava.com/api/v3/activities/{item}/streams",
                headers=headers,
                params={"keys": ["heartrate"]},
            )
            for item in result.json():
                if item.get("type") == "heartrate":
                    d["heartrate_stream"] = item.get("data")

            # extract row count from description
            if "rows" in d.get("description", ""):
                d["rows"] = int(d["description"].split("\n")[0].split(" ")[0])
                d["rpm"] = round(d["rows"] / d["moving_time"] * 60, 2)

            activities.append(d)

    json.dump(activities, open("rowing_activities.json", "w"), indent=2)


# main()
print(update_data())
