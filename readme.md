## workout statistics of @mfa

### about

- download rowing workouts from Strava
- store them in sqlite
- add dashboards for rows-per-minute and minutes-per-week

### some notes

- my Strava workouts are private (need "activity:read_all" to read them)
- Strava authentication flow is a bit messy -- a browser is needed for to get the `refresh_token`
- add with `client_id` and `client_secret` to `_secrets.json` -- to get this a strava app is needed: <https://www.strava.com/settings/api>
- first run gets new `refresh_token` and adds this to `_secrets.json`

more information on Strava authentication: <http://developers.strava.com/docs/authentication/>
