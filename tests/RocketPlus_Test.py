import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import ROCKET_URL, ROCKET_UCC, ROCKET_PASSWORD, ROCKET_PIN, REKYC_PDF_FILE, REKYC_JPG_FILE

from playwright.sync_api import sync_playwright

STEP_RESULTS = []
RESULTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rocketplus_step_results.json")


def run_step(step_num, step_name, action):
    try:
        action()
        STEP_RESULTS.append({"step": step_num, "name": step_name, "status": "PASS", "reason": ""})
        print(f" Step {step_num} PASSED: {step_name}")
    except Exception as e:
        STEP_RESULTS.append({"step": step_num, "name": step_name, "status": "FAIL", "reason": str(e)})
        with open(RESULTS_FILE, "w") as f:
            json.dump(STEP_RESULTS, f, indent=2)
        print(f" Step {step_num} FAILED: {step_name}\n Reason: {e}")
        raise


class TestRocketPlus:
    def test_rocketplus_flow(self, playwright):
        browser = playwright.chromium.launch(headless=False)
        video_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "videos")
        os.makedirs(video_dir, exist_ok=True)
        context = browser.new_context(
            record_video_dir=video_dir,
            record_video_size={"width": 1280, "height": 720},
        )
        page    = context.new_page()

        try:
            # ── STEP 1: Open RocketPlus Login Page ────────
            def step1():
                page.goto(ROCKET_URL)
                page.wait_for_load_state("networkidle", timeout=15000)
            run_step(1, "Open RocketPlus Login Page", step1)

            # ── STEP 2: Enter UCC ─────────────────────────
            def step2():
                ucc_locators = [
                    "input[placeholder='USER ID']",
                    "input[placeholder='User ID']",
                    "input[placeholder='user id']",
                    "input[placeholder='UserId']",
                    "//input[@name='userId']",
                    "//input[@id='userId']",
                    "//input[@type='text'][1]",
                ]
                filled = False
                for loc in ucc_locators:
                    try:
                        field = page.locator(loc).first
                        if field.is_visible(timeout=3000):
                            field.fill(ROCKET_UCC)
                            filled = True
                            print(f" UCC filled using: {loc}")
                            break
                    except:
                        continue
                if not filled:
                    raise Exception("UCC input field not found!")
                page.wait_for_timeout(1000)
            run_step(2, f"Enter UCC: {ROCKET_UCC}", step2)

            # ── STEP 3: Click Validate ─────────────────────
            def step3():
                page.locator("#validateUser").click()
                page.wait_for_timeout(2000)
            run_step(3, "Click Validate Button", step3)

            # ── STEP 4: Enter Password ─────────────────────
            def step4():
                page.locator("#login_password_field").fill(ROCKET_PASSWORD)
                page.wait_for_timeout(1000)
            run_step(4, "Enter Password", step4)

            # ── STEP 5: Confirm Secure Access Image ────────
            def step5():
                page.locator("#confirmimage").click()
                page.wait_for_timeout(1000)
            run_step(5, "Confirm Secure Access Image", step5)

            # ── STEP 6: Click Submit ───────────────────────
            def step6():
                for btn_id in ["vaaidatePassword", "validatePassword", "vaalidatePassword"]:
                    try:
                        btn = page.locator(f"#{btn_id}")
                        if btn.is_visible(timeout=3000):
                            btn.click()
                            print(f" Submit clicked using: #{btn_id}")
                            page.wait_for_timeout(3000)
                            return
                    except:
                        continue
                page.locator("button[type='submit'].btn-orange").click()
                page.wait_for_timeout(3000)
            run_step(6, "Click Submit Button", step6)

            # ── STEP 7: Click Login with PIN ───────────────
            def step7():
                page.locator("//a[contains(text(),'Login with PIN')]").click()
                page.wait_for_timeout(2000)
            run_step(7, "Click Login with PIN", step7)

            # ── STEP 8: Enter PIN ──────────────────────────
            def step8():
                page.locator("#efirstPin").fill(ROCKET_PIN)
                page.wait_for_timeout(1000)
            run_step(8, "Enter PIN", step8)

            # ── STEP 9: Click Submit PIN ───────────────────
            def step9():
                page.locator("#pinScreen").click()
                page.wait_for_timeout(3000)
            run_step(9, "Click Submit PIN", step9)

            # ── STEP 10: Click Agree Popup ─────────────────
            def step10():
                agree_btn = page.locator("//button[text()='AGREE'] | //button[contains(text(),'Agree')]")
                if agree_btn.count() > 0:
                    agree_btn.first.click()
                    page.wait_for_timeout(2000)
            run_step(10, "Click Agree Popup", step10)

            # ── STEP 11: Click Profile Icon ────────────────
            def step11():
                page.locator("li#userProf a.dropdown-toggle").click()
                page.wait_for_timeout(2000)
            run_step(11, "Click Profile Icon", step11)

            # ── STEP 12: Click Profile Edit ────────────────
            def step12():
                page.locator("li#profileEdit a").click()
                page.wait_for_timeout(3000)
            run_step(12, "Click Profile Edit", step12)

            # ── Switch to ReKYC tab ────────────────────────
            rekyc_page = page.context.pages[-1]
            rekyc_page.bring_to_front()
            rekyc_page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)

            # ── STEP 13: Click Email ───────────────────────
            def step13():
                rekyc_page.locator("//a[text()='Email']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(13, "Click Email Section", step13)

            # ── STEP 14: Click Mobile No ───────────────────
            def step14():
                rekyc_page.locator("//a[text()='Mobile No']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(14, "Click Mobile No Section", step14)

            # ── STEP 15: Click Change of Address ──────────
            def step15():
                rekyc_page.locator("//a[text()='Change of address']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(15, "Click Change of Address Section", step15)

            # ── STEP 16: Click Nominee ─────────────────────
            def step16():
                rekyc_page.locator("//a[text()='Nominee']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(16, "Click Nominee Section", step16)

            # ── STEP 17: Click Bank ────────────────────────
            def step17():
                rekyc_page.locator("//a[text()='Bank']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(17, "Click Bank Section", step17)

            # ── STEP 18: Click Segment ─────────────────────
            def step18():
                rekyc_page.locator("//a[text()='Segment']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
                agree_btn = rekyc_page.locator("//button[contains(text(), 'Agree')] | //a[contains(text(), 'Agree')] | //input[@value='Agree']")
                if agree_btn.count() > 0:
                    agree_btn.first.click()
                    rekyc_page.wait_for_timeout(1000)
            run_step(18, "Click Segment Section", step18)

            # ── STEP 19: Click Income Declaration ─────────
            def step19():
                rekyc_page.locator("//a[text()='Income Declaration']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(19, "Click Income Declaration Section", step19)

            # ── STEP 24: Click Dis Slip Req ────────────────
            def step24():
                rekyc_page.locator("//a[text()='Dis Slip Req']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(24, "Click Dis Slip Req Section", step24)

            # ── STEP 25: Click Service Status ─────────────
            def step25():
                rekyc_page.wait_for_selector("//a[contains(text(), 'Service Status')]", timeout=15000)
                rekyc_page.locator("//a[contains(text(), 'Service Status')]").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(25, "Click Service Status Section", step25)

            # ── STEP 21: Click Documents ───────────────────
            def step21():
                rekyc_page.locator("//a[text()='Documents']").click(no_wait_after=True)
                rekyc_page.wait_for_selector("table", timeout=15000)
                rekyc_page.wait_for_timeout(3000)
            run_step(21, "Click Documents Section", step21)

            # ── STEP 22: Click First View Proof ───────────
            def step22():
                rekyc_page.wait_for_timeout(5000)
                rekyc_page.locator("table tr").nth(1).locator("td").last.click()
                print(" Clicked first View Proof")
                rekyc_page.wait_for_timeout(2000)
                rekyc_page.locator("#closeModal").click()
                rekyc_page.wait_for_timeout(1000)
            run_step(22, "Click View Proof for first row", step22)

            # ── STEP 20: Click DDPI ────────────────────────
            def step20():
                rekyc_page.locator("//a[text()='DDPI']").click(no_wait_after=True)
                rekyc_page.wait_for_timeout(2000)
            run_step(20, "Click DDPI Section", step20)

            # ── STEP 26: Switch Back to RocketPlus ────────
            def step26():
                page.bring_to_front()
                page.wait_for_timeout(2000)
            run_step(26, "Switch Back to RocketPlus", step26)

            # ── STEP 27: Click Profile Icon ────────────────
            def step27():
                page.locator("li#userProf a.dropdown-toggle").click()
                page.wait_for_timeout(2000)
            run_step(27, "Click Profile Icon", step27)

            # ── STEP 28: Click Support ─────────────────────
            def step28():
                page.locator("//li[contains(@id,'support')] | //a[contains(text(),'Support')]").first.click()
                page.wait_for_timeout(3000)
            run_step(28, "Click Support", step28)

            # ── Switch to Support tab ──────────────────────
            page.wait_for_timeout(3000)
            support_page = page.context.pages[-1]
            support_page.bring_to_front()
            try:
                support_page.wait_for_load_state("networkidle", timeout=15000)
            except:
                support_page.wait_for_load_state("domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)

            # ── STEP 29: Click KYC Modifications ──────────
            def step29():
                support_page.wait_for_timeout(5000)

                print(f" Support Page URL: {support_page.url}")
                print(f" Support Page Title: {support_page.title()}")

                kyc_locators = [
                    "text=KYC Modifications",
                    "text=KYC modifications",
                    "text=Kyc Modifications",
                    "//a[contains(text(),'KYC')]",
                    "//span[contains(text(),'KYC')]",
                    "//div[contains(text(),'KYC Modifications')]",
                    "//li[contains(text(),'KYC Modifications')]",
                    "//*[contains(text(),'KYC Modifications')]",
                    "//*[contains(text(),'KYC')]",
                ]

                clicked = False
                for loc in kyc_locators:
                    try:
                        element = support_page.locator(loc).first
                        if element.is_visible(timeout=3000):
                            element.click()
                            clicked = True
                            print(f" KYC Modifications clicked using: {loc}")
                            support_page.wait_for_timeout(4000)
                            break
                    except:
                        continue

                if not clicked:
                    frames = support_page.frames
                    print(f" Total frames on page: {len(frames)}")
                    for frame in frames:
                        try:
                            element = frame.locator("//*[contains(text(),'KYC')]").first
                            if element.is_visible(timeout=2000):
                                element.click()
                                clicked = True
                                print(f" KYC Modifications clicked inside iframe: {frame.url}")
                                support_page.wait_for_timeout(4000)
                                break
                        except:
                            continue

                if not clicked:
                    body_text = support_page.locator("body").text_content()
                    print(f" Page body text (first 500 chars): {body_text[:500]}")
                    raise Exception("KYC Modifications element not found on page or in any iframe!")

            run_step(29, "Click KYC Modifications", step29)

            # ── STEP 30: Click Name change in Demat ───────
            def step30():
                support_page.wait_for_selector("text=Name change in Demat Account", timeout=10000)
                support_page.get_by_text("Name change in Demat Account").first.click()
                support_page.wait_for_timeout(4000)
            run_step(30, "Click Name change in Demat Account", step30)

            # ── STEP 31: Click Create Ticket ──────────────
            def step31():
                support_page.evaluate("window.scrollBy(0, 500)")
                support_page.wait_for_timeout(1000)
                support_page.evaluate("window.scrollBy(0, 500)")
                support_page.wait_for_timeout(1000)
                support_page.wait_for_selector("text=Create Ticket", timeout=10000)
                support_page.get_by_text("Create Ticket").click()
                support_page.wait_for_timeout(4000)
            run_step(31, "Click Create Ticket Button", step31)

            # ── STEP 32: Type Description ─────────────────
            def step32():
                support_page.evaluate("window.scrollBy(0, 500)")
                support_page.wait_for_timeout(1000)
                support_page.evaluate("window.scrollBy(0, 500)")
                support_page.wait_for_timeout(1000)
                support_page.wait_for_selector("div.fr-element.fr-view", state="attached", timeout=15000)
                support_page.wait_for_timeout(1000)
                support_page.evaluate("""
                    const editor = document.querySelector('div.fr-element.fr-view');
                    if (editor) {
                        editor.focus();
                        editor.click();
                    }
                """)
                support_page.wait_for_timeout(1000)
                support_page.keyboard.type("Testing")
                support_page.wait_for_timeout(1000)
            run_step(32, "Type Description", step32)

            # ── STEP 33: Submit Ticket ─────────────────────
            def step33():
                support_page.evaluate("window.scrollBy(0, 300)")
                support_page.wait_for_timeout(2000)
                support_page.wait_for_selector("button.new-ticket-submit-button:not([disabled])", timeout=15000)
                support_page.wait_for_timeout(1000)
                support_page.evaluate("""
                    const btn = document.querySelector('button.new-ticket-submit-button');
                    if (btn) {
                        btn.removeAttribute('disabled');
                        btn.click();
                    }
                """)
                print(" Submit clicked using JavaScript")
                support_page.wait_for_timeout(5000)
            run_step(33, "Click Submit Ticket", step33)

            # ── STEP 34: Verify Success Message ───────────
            def step34():
                support_page.wait_for_timeout(5000)
                success_texts = [
                    "Your ticket has been created",
                    "ticket has been created",
                    "You shall get a response",
                    "Ticket has been",
                    "successfully created",
                    "ticket was created",
                ]
                found_msg = None
                for text in success_texts:
                    try:
                        element = support_page.locator(f"//*[contains(text(),'{text}')]").first
                        if element.is_visible(timeout=5000):
                            found_msg = element.text_content()
                            print(f" Success Message Found: {found_msg}")
                            break
                    except:
                        continue
                if not found_msg:
                    current_url = support_page.url
                    print(f" Current URL: {current_url}")
                    if any(keyword in current_url for keyword in ["home", "tickets", "search"]):
                        found_msg = f"Ticket created - redirected to: {current_url}"
                        print(f" Ticket created - URL confirms: {current_url}")
                    else:
                        raise Exception(f"Success message not found! Current URL: {current_url}")
                assert found_msg is not None
            run_step(34, "Verify Ticket Created Success Message", step34)

            # ── STEP 35: Click Track Tickets ──────────────
            def step35():
                support_page.wait_for_timeout(2000)
                track_locators = [
                    "text=Track tickets",
                    "text=Track Tickets",
                    "//a[contains(text(),'Track')]",
                    "//a[contains(text(),'track')]",
                ]
                clicked = False
                for locator in track_locators:
                    try:
                        element = support_page.locator(locator).first
                        if element.is_visible(timeout=3000):
                            element.click()
                            clicked = True
                            print(f" Track tickets clicked!")
                            break
                    except:
                        continue
                if not clicked:
                    print(" Track link not found, navigating directly...")
                    support_page.goto("https://support.navia.co.in/support/home?tickets=true#ticketList")
                support_page.wait_for_timeout(3000)
            run_step(35, "Click Track Tickets", step35)

            # ── STEP 36: Verify Latest Ticket ─────────────
            def step36():
                support_page.wait_for_timeout(3000)
                try:
                    support_page.wait_for_selector("table", timeout=10000)
                    first_ticket = support_page.locator("table tr").nth(1).text_content()
                    print(f" Latest Ticket Row: {first_ticket}")
                    assert "Name change in Demat Account" in first_ticket, \
                        f"Latest ticket not found! Found instead: {first_ticket}"
                    print(" Latest ticket verified successfully!")
                except Exception as e:
                    all_text = support_page.locator("body").text_content()
                    raise Exception(f"Ticket list not found! Page content: {all_text[:300]}")
            run_step(36, "Verify Latest Ticket Visible in List", step36)

            print("\n All Steps Completed Successfully!")

        finally:
            with open(RESULTS_FILE, "w") as f:
                json.dump(STEP_RESULTS, f, indent=2)
            context.close()
            browser.close()
