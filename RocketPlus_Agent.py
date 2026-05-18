import ast
import datetime
import html
import json
import os
import smtplib
import subprocess
import sys
import time

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


PROJECT_FOLDER_NAME = "RocketPlus_Test"
TEST_FILE = os.path.join("tests", "RocketPlus_Test.py")
RESULTS_FILE = "rocketplus_step_results.json"


def header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def line():
    print("-" * 60)


def find_project_folder():
    header("STEP 1 | AUTO-LOCATING PROJECT FOLDER")

    current_dir = os.path.abspath(os.path.dirname(__file__))
    if os.path.exists(os.path.join(current_dir, TEST_FILE)):
        print("  [OK] Project folder found:")
        print(f"       {current_dir}")
        return current_dir

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", PROJECT_FOLDER_NAME)
    if os.path.exists(os.path.join(desktop_path, TEST_FILE)):
        print("  [OK] Project folder found on Desktop:")
        print(f"       {desktop_path}")
        return desktop_path

    desktop_root = os.path.join(os.path.expanduser("~"), "Desktop")
    print(f"  [..] Searching Desktop for {PROJECT_FOLDER_NAME}...")
    for root, _, files in os.walk(desktop_root):
        if "RocketPlus_Test.py" in files:
            project_path = os.path.dirname(root) if os.path.basename(root).lower() == "tests" else root
            print("  [OK] Project folder found:")
            print(f"       {project_path}")
            return project_path

    print("  [ERROR] Could not find RocketPlus project folder.")
    print("  [i] Place RocketPlus_Agent.py inside the RocketPlus_Test folder and run again.")
    input("\n  Press Enter to close...")
    sys.exit(1)


def syntax_check(path, label):
    print(f"  [i] File : {label}")
    with open(path, "r", encoding="utf-8") as file:
        code = file.read()

    try:
        ast.parse(code)
        print("  [OK] Syntax Check : No errors found")
    except SyntaxError as exc:
        print(f"  [ERROR] Syntax Issue : Line {exc.lineno} - {exc.msg}")
        input("\n  Fix the error and run again. Press Enter to close...")
        sys.exit(1)

    return code


def review_test_code(project_path):
    header("STEP 2 | REVIEWING TEST CODE")

    test_path = os.path.join(project_path, TEST_FILE)
    config_path = os.path.join(project_path, "config.py")

    for relative_path, full_path in [
        (TEST_FILE, test_path),
        ("config.py", config_path),
    ]:
        if not os.path.exists(full_path):
            print(f"  [ERROR] Missing file : {relative_path}")
            input("\n  Press Enter to close...")
            sys.exit(1)
        syntax_check(full_path, relative_path)

    with open(test_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)
    test_functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]

    print(f"  [OK] Test Functions    : {len(test_functions)} found")
    for name in test_functions:
        print(f"       -> {name}")
    print(f"  [OK] Total Lines       : {len(source_code.splitlines())}")
    print("  [OK] Config File       : config.py found")
    print(
        "  [OK] Step Results File : "
        + ("found" if os.path.exists(os.path.join(project_path, RESULTS_FILE)) else "will be created after test run")
    )
    print("\n  [OK] Code Review Complete - Ready to run!")


def run_tests(project_path):
    header("STEP 3 | RUNNING PYTEST AUTOMATICALLY")

    start_time = time.time()
    started = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    command = [sys.executable, "-m", "pytest", "tests", "-s"]

    print(f"  [i] Started : {started}")
    print("  [i] Running : pytest tests/ -s")
    print("  [i] LIVE OUTPUT")
    line()

    process = subprocess.Popen(
        command,
        cwd=project_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    output_lines = []
    for output_line in process.stdout:
        print(output_line, end="")
        output_lines.append(output_line.rstrip())

    exit_code = process.wait()
    elapsed = int(time.time() - start_time)
    duration = f"{elapsed // 60}m {elapsed % 60}s"
    status = "PASS" if exit_code == 0 else "FAIL"

    print("\n  [OK] Execution Completed")
    print(f"  [OK] Status   : {status}")
    print(f"  [OK] Duration : {duration}")

    return exit_code, status, duration, output_lines


def read_step_results(project_path):
    json_path = os.path.join(project_path, RESULTS_FILE)
    if not os.path.exists(json_path):
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        print(f"  [ERROR] Could not read {RESULTS_FILE}: {exc}")
        return []


def find_latest_video(project_path):
    search_dirs = [
        os.path.join(project_path, "reports", "videos"),
        os.path.join(project_path, "test-results"),
        os.path.join(project_path, "reports"),
        os.path.join(project_path, "videos"),
    ]
    videos = []

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        for root, _, files in os.walk(search_dir):
            for file_name in files:
                if file_name.lower().endswith((".webm", ".mp4")):
                    videos.append(os.path.join(root, file_name))

    if not videos:
        return None

    return max(videos, key=os.path.getmtime)


def find_latest_video_attachment(project_path):
    video_root = os.path.join(project_path, "videos")
    if not os.path.exists(video_root):
        return find_latest_video(project_path)

    videos = []
    for root, _, files in os.walk(video_root):
        for file_name in files:
            if file_name.lower().endswith((".webm", ".mp4")):
                videos.append(os.path.join(root, file_name))

    if not videos:
        return find_latest_video(project_path)

    return max(videos, key=os.path.getmtime)


def attach_file(message, file_path):
    if not file_path or not os.path.exists(file_path):
        return False

    with open(file_path, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(file_path)}",
    )
    message.attach(part)
    return True


def send_mail(project_path, status, duration, steps, output_lines, video_path):
    if project_path not in sys.path:
        sys.path.insert(0, project_path)

    try:
        from config import EMAIL_REPORT
    except Exception as exc:
        print(f"  [ERROR] Email config not found: {exc}")
        return

    receivers = EMAIL_REPORT.get("receiver", [])
    if isinstance(receivers, str):
        receivers = [receivers]

    step_rows = ""
    for step in steps:
        step_status = str(step.get("status", ""))
        color = "#dcfce7" if step_status == "PASS" else "#fee2e2"
        step_rows += f"""
        <tr style="background:{color}">
            <td>{html.escape(str(step.get('step', '')))}</td>
            <td>{html.escape(step_status)}</td>
            <td>{html.escape(str(step.get('name', '')))}</td>
            <td>{html.escape(str(step.get('reason', '')))}</td>
        </tr>
        """

    if not step_rows:
        step_rows = "<tr><td colspan='4'>No step data found.</td></tr>"

    video_line = "Attached to this email" if video_path else "No video file found"
    safe_video_path = html.escape(video_path) if video_path else ""
    color = "#16a34a" if status == "PASS" else "#dc2626"

    email_html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;padding:20px;color:#222">
        <h2>RocketPlus Automation Report</h2>
        <p><b>Code Review:</b> PASS</p>
        <p><b>Test Execution:</b> <span style="color:{color}"><b>{html.escape(status)}</b></span></p>
        <p><b>Duration:</b> {html.escape(duration)}</p>

        <h3>Step Results</h3>
        <table style="border-collapse:collapse;width:100%;font-size:13px">
            <tr style="background:#f3f4f6">
                <th style="padding:4px;border:1px solid #888">Step</th>
                <th style="padding:4px;border:1px solid #888">Status</th>
                <th style="padding:4px;border:1px solid #888">Name</th>
                <th style="padding:4px;border:1px solid #888">Reason</th>
            </tr>
            {step_rows}
        </table>

        <p><b>Video:</b> {video_line}</p>
        {f"<p><b>Video File:</b> {safe_video_path}</p>" if video_path else ""}
    </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = EMAIL_REPORT["sender"]
    message["To"] = ", ".join(receivers)
    message["Subject"] = f"RocketPlus Automation Report - {status}"
    message.attach(MIMEText(email_html, "html"))

    attached = attach_file(message, video_path)

    current_dir = os.getcwd()
    os.chdir(project_path)
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_REPORT["sender"], EMAIL_REPORT["password"])
        server.send_message(message)
        server.quit()
        print("  [OK] EMAIL SENT SUCCESSFULLY")
        if attached:
            print(f"  [OK] VIDEO ATTACHED: {video_path}")
    except Exception as exc:
        print(f"  [ERROR] EMAIL FAILED: {exc}")
    finally:
        os.chdir(current_dir)


def review_report(project_path, exit_code, status, duration, output_lines):
    header("STEP 4 | AGENT REPORT REVIEW")

    steps = read_step_results(project_path)
    passed = [step for step in steps if step.get("status") == "PASS"]
    failed = [step for step in steps if step.get("status") != "PASS"]
    video_path = find_latest_video_attachment(project_path)

    print(f"  OVERALL RESULT : {status}")
    print(f"  EXIT CODE      : {exit_code}")
    print(f"  DURATION       : {duration}")
    print(f"  LOG LINES      : {len(output_lines)}")
    print(f"  VIDEO          : {video_path if video_path else 'No video found'}")
    print(f"  TOTAL STEPS    : {len(steps)}")
    print(f"  PASSED         : {len(passed)}")
    print(f"  FAILED         : {len(failed)}")

    line()
    print("\n  FAILED STEPS:")
    if failed:
        for step in failed:
            reason = step.get("reason") or "No reason provided"
            print(f"    Step {str(step.get('step', '')).zfill(2)} [FAIL] {step.get('name', '')}")
            print(f"         Reason: {reason}")
    else:
        print("    None - All steps passed.")

    line()
    print("\n  AGENT VERDICT:")
    if status == "PASS" and not failed:
        print("    RocketPlus automation completed successfully.")
    else:
        print("    RocketPlus automation completed with failure.")
        print("    Check the failed steps and live output above.")

    header("STEP 5 | SENDING EMAIL REPORT")
    send_mail(project_path, status, duration, steps, output_lines, video_path)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("   ROCKETPLUS AUTOMATION AGENT")
    print("   Fully Automatic - No manual steps needed")
    print("=" * 60)
    print(f"   Started : {datetime.datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")

    project = find_project_folder()
    review_test_code(project)
    code, final_status, total_duration, logs = run_tests(project)
    review_report(project, code, final_status, total_duration, logs)

    header("AGENT COMPLETE")
    print(f"  Finished : {datetime.datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")
    print("  Full summary shown above")
    print("=" * 60)

    input("\n  Press Enter to close...\n")
