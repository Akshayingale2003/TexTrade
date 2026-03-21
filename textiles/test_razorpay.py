import razorpay

RAZORPAY_KEY_ID = "rzp_test_STYwRIPZrMl5Yo"
RAZORPAY_KEY_SECRET = "gDFQ5L8XybXOt1MfeSp2zVTe"

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

try:
    client.payment.all()
    print("Authentication successful! Keys are correct.")
except razorpay.errors.BadRequestError:
    print("Authentication failed! Check your Razorpay keys.")
