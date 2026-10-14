"""Generate reproducible synthetic support FAQs, policy docs, and evaluation questions."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

faqs = [
("How can I return an item?", "Start a return from the Orders page within 30 days of delivery. The item must be unused and include original packaging. Keep the return reference for tracking.", "returns", "returns_faq"),
("When will my refund arrive?", "After the returned item passes inspection, refunds are initiated to the original payment method. Allow 5 to 7 business days after initiation for the payment provider to post the refund.", "refunds", "refunds_faq"),
("Can I cancel an order after it ships?", "Orders that have shipped cannot normally be cancelled. You may request a return after delivery if the item meets the return conditions.", "orders", "orders_faq"),
("How do I track my shipment?", "Open Orders, select the order, and choose Track shipment. Tracking updates may take up to 24 hours after dispatch.", "shipping", "shipping_faq"),
("My package is late. What should I do?", "Check the tracking page first. If tracking has not changed for 48 hours after the estimated delivery date, contact support with the order reference.", "shipping", "shipping_faq"),
("What should I do if an item arrives damaged?", "Photograph the damaged item and packaging, then contact support within 48 hours of delivery. Do not discard packaging until support responds.", "damaged_item", "returns_faq"),
("How do I change my delivery address?", "An address can be changed before the order is packed. Open Orders and check whether Edit address is available; otherwise contact support promptly.", "orders", "orders_faq"),
("Why was my payment declined?", "Confirm the billing details and available balance with your payment provider. Do not send card numbers or security codes to support. Try another approved payment method if needed.", "payments", "payments_faq"),
("How can I reset my password?", "Choose Forgot password on the sign-in page. Follow the reset link sent to your registered email. Never share the reset link or one-time code with another person.", "account", "account_faq"),
("I cannot sign in to my account.", "Check that the email address is correct and reset your password if needed. If the account remains locked after the reset, contact account support for verification.", "account", "account_faq"),
("How do I contact a human support agent?", "Use the Help section and select Contact support. Include a short description and order reference, but never include passwords or full payment-card details.", "support", "support_faq"),
("Can I return a final-sale item?", "Final-sale items are not eligible for change-of-mind returns in this demonstration policy. Items damaged in transit should still be reported to support for review.", "returns", "returns_faq"),
("What if I received the wrong item?", "Keep the item and packaging, take a photo of the item label, and contact support within 7 days of delivery so the issue can be reviewed.", "wrong_item", "returns_faq"),
("Are weekend days counted for refunds?", "The refund estimate is expressed in business days, so weekends and public holidays are not counted.", "refunds", "refunds_faq"),
("How do I update my email address?", "Open Account settings and choose Update email. Complete the verification steps sent to your current and new email addresses.", "account", "account_faq"),
("I was charged twice for one order.", "Check whether one entry is a pending authorisation. If both charges are posted, contact payment support with the order reference and transaction dates; do not send full card details.", "payments", "payments_faq"),
("Can I change an item after placing an order?", "Changes may be possible before packing begins. Check the order page for Edit options or contact support immediately.", "orders", "orders_faq"),
("The tracking page says delivered but I did not receive it.", "Check the delivery location and ask household members or building reception. If the parcel is still missing, contact support with the order reference for an investigation.", "shipping", "shipping_faq"),
("How do I report a suspicious message?", "Do not click links or share passwords or one-time codes. Forward the message using the official security-reporting option in the Help section.", "security", "security_faq"),
("What details should I include in a support request?", "Include the order reference, a concise description, relevant dates, and non-sensitive screenshots if appropriate. Never provide passwords, one-time codes, or full payment-card details.", "support", "support_faq"),
]
with (RAW / "support_faqs.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["doc_id", "question", "answer", "category", "source"])
    w.writeheader()
    for i, (q, a, cat, src) in enumerate(faqs, 1):
        w.writerow({"doc_id": f"FAQ-{i:03d}", "question": q, "answer": a, "category": cat, "source": f"{src}.txt"})

policies = [
{"doc_id":"POL-001","title":"Return Policy","category":"returns","source":"return_policy.txt","content":"Demonstration policy: Most unused items may be returned within 30 days of delivery in original packaging. Final-sale items are not eligible for change-of-mind returns. Damaged or incorrect items should be reported within the relevant reporting window in the support FAQ. This is synthetic training data, not a real company policy."},
{"doc_id":"POL-002","title":"Refund Policy","category":"refunds","source":"refund_policy.txt","content":"Demonstration policy: Refunds are initiated after return inspection and sent to the original payment method. Payment providers may take 5 to 7 business days after initiation. Business days exclude weekends and public holidays. Pending authorisations may disappear without becoming a posted charge."},
{"doc_id":"POL-003","title":"Shipping and Delivery Guide","category":"shipping","source":"shipping_guide.txt","content":"Demonstration guide: Use the order page to track shipments. Tracking may take up to 24 hours to update after dispatch. If tracking remains unchanged for 48 hours after the estimated delivery date, contact support. For a delivered-but-missing parcel, check nearby safe locations and building reception before requesting an investigation."},
{"doc_id":"POL-004","title":"Account Security Guide","category":"security","source":"account_security.txt","content":"Never share passwords, reset links, one-time codes, or full payment-card details. Use the official password-reset flow. Report suspicious messages through the official support channel. Support should never request a user's password or one-time authentication code."},
{"doc_id":"POL-005","title":"Human Escalation Procedure","category":"support","source":"escalation_procedure.txt","content":"Escalate to human support when the answer is not supported by the knowledge base, a payment appears to have been posted twice, an account remains locked after standard recovery, the customer reports a safety or security concern, or the customer expresses high urgency or severe dissatisfaction. Collect only necessary non-sensitive details."}
]
with (RAW / "policies.jsonl").open("w", encoding="utf-8") as f:
    for p in policies:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")

evals = [
("How long do I have to return an unused item?", "30 days", "POL-001"),
("How long can a refund take after initiation?", "5 to 7 business days", "POL-002"),
("What do I do if tracking has not changed after the delivery estimate?", "Contact support after 48 hours", "POL-003"),
("Should I share my one-time code with a support agent?", "No", "POL-004"),
("When should a customer issue be escalated?", "Unsupported answer, posted duplicate charge, account recovery failure, security concern, or high urgency", "POL-005"),
("How do I reset my password?", "Use Forgot password and follow the registered email reset link", "account_faq"),
("What if the parcel is marked delivered but is missing?", "Check nearby locations and contact support for investigation", "shipping_faq"),
("Can I return a final-sale item because I changed my mind?", "No, not under the synthetic demonstration policy", "returns_faq"),
("How do I report a suspicious message?", "Use the official security-reporting option", "security_faq"),
("What should I do about a double posted charge?", "Contact payment support with order reference and transaction dates", "payments_faq"),
]
with (RAW / "evaluation_questions.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["question", "expected_answer", "expected_source"])
    w.writeheader()
    for q, a, s in evals:
        w.writerow({"question": q, "expected_answer": a, "expected_source": s})
print(f"Generated {len(faqs)} synthetic FAQs, {len(policies)} policy docs, {len(evals)} evaluation questions in {RAW}")
