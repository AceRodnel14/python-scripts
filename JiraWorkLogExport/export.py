import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import pytz
from dateutil.rrule import rrule, DAILY
import csv
import json

# === Load config ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# === Configuration from config.json ===
jira_domain = config["jira_domain"]
email = config["email"]
api_token = config["api_token"]
timezone_str = config.get("timezone_str", "UTC")
number_of_holidays = config.get("number_of_holidays", 0)
start_month = config["start_month"]
end_month = config["end_month"]

# === Constants ===
WORK_HOURS_PER_DAY = 7
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# === Timezone Handling ===
tz = pytz.timezone(timezone_str)
start_date = tz.localize(datetime.fromisoformat(start_month))
end_date = tz.localize(datetime.fromisoformat(end_month).replace(hour=23, minute=59, second=59))

# === Function to calculate required work hours ===
def calculate_required_work_hours(start_date, end_date, holiday_count=0):
    workdays = 0
    for dt in rrule(DAILY, dtstart=start_date.date(), until=end_date.date()):
        if dt.weekday() < 5:  # Monday–Friday
            workdays += 1
    total_required_hours = (workdays - holiday_count) * WORK_HOURS_PER_DAY
    return total_required_hours, workdays

worklog_author = email  # or a username like "user.name"

auth = HTTPBasicAuth(email, api_token)
headers = {"Accept": "application/json"}

# === Prepare CSV Output ===
csv_filename = f"generated_{start_month}_{end_month}.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Ticket", "Date", "Hours", "Comment"])  # CSV Header

    # === Step 1: Search Issues with JQL ===
    search_url = f"{jira_domain}/rest/api/3/search/jql"
    jql = f'worklogAuthor = "{worklog_author}" AND worklogDate >= "{start_month}" AND worklogDate <= "{end_month}"'
    params = {
        "jql": jql,
        "fields": "key,summary",
        "maxResults": 100
    }

    print("🔍 Fetching issues with worklogs...")
    search_response = requests.get(search_url, params=params, auth=auth, headers=headers)

    if search_response.status_code != 200:
        print(f"❌ Error searching issues: {search_response.status_code}")
        print(search_response.text)
        exit(1)

    issues = search_response.json().get("issues", [])
    print(f"✅ Found {len(issues)} issues.\n")

    grand_total_seconds = 0

    # === Step 2: Loop over issues ===
    for issue in issues:
        issue_key = issue["key"]
        summary = issue["fields"]["summary"]

        worklog_url = f"{jira_domain}/rest/api/3/issue/{issue_key}/worklog"
        response = requests.get(worklog_url, auth=auth, headers=headers)

        if response.status_code != 200:
            print(f"⚠️  Could not retrieve worklogs for {issue_key}")
            continue

        worklogs = response.json().get("worklogs", [])
        issue_total_seconds = 0
        matched_worklogs = []

        for wl in worklogs:
            author_info = wl.get("author", {})
            author_email = author_info.get("emailAddress", "unknown")
            started_str = wl.get("started", "")
            time_spent_seconds = wl.get("timeSpentSeconds", 0)
            comment = wl.get("comment", {}).get("content", "")

            try:
                started_dt_utc = datetime.strptime(started_str, "%Y-%m-%dT%H:%M:%S.%f%z")
                started_dt_local = started_dt_utc.astimezone(tz)
            except Exception as e:
                print(f"❌ Could not parse date: {started_str} — {e}")
                continue

            if author_email == worklog_author and start_date <= started_dt_local <= end_date:
                matched_worklogs.append((started_dt_local.date(), time_spent_seconds))
                issue_total_seconds += time_spent_seconds

                # Flatten Jira comment format (rich text content)
                plain_comment = ""
                if isinstance(comment, list):
                    for block in comment:
                        for part in block.get("content", []):
                            plain_comment += part.get("text", "")
                elif isinstance(comment, str):
                    plain_comment = comment

                csv_writer.writerow([
                    issue_key,
                    started_dt_local.date(),
                    round(time_spent_seconds / 3600, 2),
                    plain_comment.strip()
                ])

        if matched_worklogs:
            print(f"📌 {issue_key} - {summary}")
            for date_logged, secs in matched_worklogs:
                print(f"   🕒 {date_logged}: {secs / 3600:.2f}h")
            print(f"   🔢 Total for {issue_key}: {issue_total_seconds / 3600:.2f}h\n")

        grand_total_seconds += issue_total_seconds

# === Final Summary ===
grand_total_hours = grand_total_seconds / 3600
total_work_days = grand_total_seconds / (WORK_HOURS_PER_DAY * 3600)

required_hours, total_weekdays = calculate_required_work_hours(start_date, end_date, number_of_holidays)
difference = required_hours - grand_total_hours
percentage_logged = (grand_total_hours / required_hours) * 100 if required_hours > 0 else 0
color = GREEN if percentage_logged >= 95 else RED

print(f"{color}📅 Required work hours from {start_month} to {end_month} (weekdays: {total_weekdays}, holidays: {number_of_holidays}): {required_hours:.2f}h")
print(f"🧾 Total hours logged by {worklog_author} in {timezone_str}: {grand_total_hours:.2f}h or {total_work_days:.2f} work days")
print(f"📊 Difference from required: {difference:.2f}h ({percentage_logged:.1f}%) {RESET}")
print(f"📁 CSV file written to: {csv_filename}")

# === Update config.json with csv_file ===
config["csv_file"] = csv_filename
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

print(f"✅ Updated config.json with csv_file: {csv_filename}")