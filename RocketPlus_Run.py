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
                <td style="padding:10px;border:1px solid #d1d5db;font-weight:700">{step.get('step','')}</td>
                <td style="padding:10px;border:1px solid #d1d5db;color:{color};font-weight:700">{s_icon} {step.get('status','')}</td>
                <td style="padding:10px;border:1px solid #d1d5db">{step.get('name','')}</td>
                <td style="padding:10px;border:1px solid #d1d5db">{step.get('reason','')}</td>
            </tr>
            """
    else:
        step_rows = "<tr><td colspan='4'>No step data found</td></tr>"

    # ✅ LOG FIX
    log_html = "\n".join(log_lines).replace("<", "&lt;").replace(">", "&gt;")

    html = f"""
    <html>
    <body style="margin:0;background:#f4f6f8;font-family:Arial,sans-serif;color:#111827">
        <div style="max-width:1080px;margin:0 auto;padding:20px">
            <div style="background:#ffffff;border:1px solid #e5e7eb">
                <div style="background:#1f3f68;color:#ffffff;padding:22px 24px">
                    <div style="font-size:22px;font-weight:700">RocketPlus Automation Report</div>
                    <div style="font-size:13px;margin-top:6px">Generated: {now} | Duration: {duration}</div>
                </div>
                <div style="padding:18px 24px 24px">
                    <div style="font-size:14px;font-weight:700;margin-bottom:14px">
                        Test Execution:
                        <span style="background:{'#dcfce7' if status == 'PASS' else '#fee2e2'};color:{color};padding:7px 18px;border-radius:5px">{status}</span>
                    </div>
                    <table style="width:100%;border-collapse:collapse;font-size:13px;margin-bottom:16px">
                        <thead>
                            <tr style="background:#344153;color:#ffffff;text-align:left">
                                <th style="padding:10px;border:1px solid #4b5563">Step</th>
                                <th style="padding:10px;border:1px solid #4b5563">Status</th>
                                <th style="padding:10px;border:1px solid #4b5563">Name</th>
                                <th style="padding:10px;border:1px solid #4b5563">Reason</th>
                            </tr>
                        </thead>
                        <tbody>{step_rows}</tbody>
                    </table>
                    <div style="font-size:13px;color:#374151;margin-bottom:10px"><b>Recording:</b> {video_path if video_path else "No recording found"}</div>
                    <div style="font-size:13px;font-weight:700;margin:14px 0 6px">Execution Logs</div>
                    <pre style="background:#111827;color:#d1fae5;padding:12px;white-space:pre-wrap;font-size:12px;line-height:1.4">{log_html}</pre>
                </div>
            </div>
        </div>
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
        server = smtplib.SMTP_SSL(EMAIL_REPORT["smtp_server"], EMAIL_REPORT["smtp_port"])
        smtp_username = EMAIL_REPORT.get("username", EMAIL_REPORT["sender"])
        server.login(smtp_username, EMAIL_REPORT["password"])
        server.sendmail(EMAIL_REPORT["sender"], receivers, msg.as_string())
        server.quit()
        print("Mail sent successfully")
    except Exception as e:
        print("Mail failed:", e)
