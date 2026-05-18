def send_report(status, video_path, log_lines, step_results, duration):

    receivers = EMAIL_REPORT["receiver"]
    if isinstance(receivers, str):
        receivers = [receivers]

    icon  = "✅" if status == "PASS" else "❌"
    color = "#16a34a" if status == "PASS" else "#dc2626"
    now   = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    subject = f"{icon} RocketPlus Automation Report - {status} | {now}"

    # ✅ STEP TABLE FIXED
    step_rows = ""
    if step_results:
        for step in step_results:
            s_icon  = "✅" if step["status"] == "PASS" else "❌"
            s_color = "#dcfce7" if step["status"] == "PASS" else "#fee2e2"

            step_rows += f"""
            <tr style="background:{s_color}">
                <td><b>{step.get('step','')}</b></td>
                <td>{s_icon} {step.get('status','')}</td>
                <td>{step.get('name','')}</td>
                <td>{step.get('reason','')}</td>
            </tr>
            """
    else:
        step_rows = "<tr><td colspan='4'>No step data found</td></tr>"

    # ✅ LOG FIX
    log_html = "\n".join(log_lines).replace("<", "&lt;").replace(">", "&gt;")

    html = f"""
    <html>
    <body style="font-family:Arial">

    <h2>RocketPlus Automation Report</h2>

    <h3>Status: {status}</h3>
    <h3>Duration: {duration}</h3>

    <h3>Step Results</h3>
    <table border="1" style="border-collapse:collapse;width:100%">
        <tr>
            <th>Step</th>
            <th>Status</th>
            <th>Name</th>
            <th>Reason</th>
        </tr>
        {step_rows}
    </table>

    <h3>Execution Logs</h3>
    <pre style="background:#111;color:#0f0;padding:10px">
{log_html}
    </pre>

    <h3>Recording</h3>
    <p>{video_path if video_path else "No recording found"}</p>

    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_REPORT["sender"]
    msg["To"] = ", ".join(receivers)
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    # VIDEO
    if video_path and os.path.exists(video_path):
        try:
            with open(video_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(video_path)}"'
            )
            msg.attach(part)
        except Exception as e:
            print("Video attach error:", e)

    # SEND MAIL
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_REPORT["sender"], EMAIL_REPORT["password"])
        server.sendmail(EMAIL_REPORT["sender"], receivers, msg.as_string())
        server.quit()
        print("Mail sent successfully")
    except Exception as e:
        print("Mail failed:", e)