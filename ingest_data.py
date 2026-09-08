import chromadb

from pathlib import Path
from chromadb.utils import embedding_functions


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = str(
    BASE_DIR / "chroma_db"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

hf_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=DB_PATH
)


collection = client.get_or_create_collection(
    name="faq_collection",
    embedding_function=hf_ef
)


# ============================================================
# FAQ DATASET
# ============================================================

sample_faq = [

    # --------------------------------------------------------
    # GENERAL FAQ GUIDE
    # --------------------------------------------------------

    "What topics does my data cover? The FAQ dataset covers orders, shipping, returns, refunds, payments, account management, customer support, and technical support.",

    "What should I know before getting started? You can find help with placing and tracking orders, shipping, returns and refunds, payment methods, account settings, customer support, and common technical issues.",

    "Summarise the key points for me. Orders can be placed and tracked through your account, eligible products can be returned within 14 days, refunds are usually processed within 5 to 7 business days, supported payment methods include major cards and selected online methods, and support is available for account and technical issues.",

    # --------------------------------------------------------
    # ORDERS
    # --------------------------------------------------------

    "How can I place an order? You can place an order by selecting a product, adding it to your cart, and completing the checkout process.",

    "Can I cancel my order? Orders can be cancelled before they are shipped. Once an order has been shipped, cancellation may no longer be possible.",

    "How can I check my order status? You can check your order status from the Orders section of your account.",

    "Can I modify my order after placing it? Orders can only be modified before processing begins. Contact customer support as soon as possible if you need to make a change.",

    "What happens if an item is out of stock? If an item is out of stock, you can check back later or enable notifications if restocking alerts are available.",


    # --------------------------------------------------------
    # SHIPPING
    # --------------------------------------------------------

    "How long does standard shipping take? Standard shipping usually takes 3 to 5 business days.",

    "How long does express shipping take? Express shipping usually takes 1 to 2 business days.",

    "How can I track my shipment? You can track your shipment using the tracking number provided in your shipping confirmation email.",

    "Do you offer international shipping? International shipping is available for selected countries. Shipping availability and fees are shown during checkout.",

    "What should I do if my package is delayed? If your package is delayed beyond the estimated delivery date, check the tracking information and contact customer support if the status does not update.",

    "What happens if my package is lost? If your package appears to be lost, contact customer support with your order and tracking information so the shipment can be investigated.",


    # --------------------------------------------------------
    # RETURNS
    # --------------------------------------------------------

    "What is the return policy? Eligible products can be returned within 14 days of delivery.",

    "Can I return an opened product? Opened products may be returned within 14 days if they meet the applicable return conditions.",

    "How do I request a return? You can request a return from your Orders section or contact customer support for assistance.",

    "How long do I have to return an item? You have 14 days from the date of delivery to return an eligible item.",

    "Are all products eligible for returns? Not every product is eligible for return. Eligibility depends on the product category and its condition.",

    "Who pays for return shipping? Return shipping fees depend on the reason for the return and the applicable return policy.",


    # --------------------------------------------------------
    # REFUNDS
    # --------------------------------------------------------

    "How long does a refund take? Refunds are generally processed within 5 to 7 business days after the returned item has been approved.",

    "When will I receive my refund? After a return is approved, the refund is sent to the original payment method.",

    "Can I get a refund without returning the product? Refunds normally require the product to be returned unless customer support approves an exception.",

    "What should I do if my refund has not arrived? If your refund has not arrived within the expected timeframe, contact customer support with your order details.",


    # --------------------------------------------------------
    # PAYMENTS
    # --------------------------------------------------------

    "What payment methods are supported? We support major credit cards, debit cards, and selected online payment methods.",

    "Is cash on delivery available? Cash on delivery is available only for eligible locations and orders.",

    "Why was my payment declined? A payment may be declined because of insufficient funds, incorrect payment information, bank restrictions, or security checks.",

    "Is my payment information secure? Payment information is processed through secure payment systems and is not stored directly by the customer support system.",

    "Can I change my payment method after placing an order? Payment methods generally cannot be changed after an order has been successfully placed.",


    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    "How do I create an account? Select the Sign Up option and provide the required information to create an account.",

    "How do I reset my password? Select Forgot Password on the login page and follow the instructions sent to your registered email address.",

    "Can I change my email address? You can change your email address from your account settings if the option is available.",

    "How do I update my delivery address? You can update your delivery address from your account settings before an order is shipped.",

    "Can I delete my account? You can request account deletion by contacting customer support.",


    # --------------------------------------------------------
    # CUSTOMER SUPPORT
    # --------------------------------------------------------

    "How can I contact customer support? You can contact customer support through the support section of the website.",

    "What are the customer support hours? Customer support is available Monday through Friday from 9 AM to 6 PM.",

    "Who is the support lead? The customer support lead is Alex AI.",

    "Where is the office located? The office is located at 123 Tech Lane, Silicon Valley.",

    "What is the office code? The internal office code is 998877.",


    # --------------------------------------------------------
    # TECHNICAL SUPPORT
    # --------------------------------------------------------

    "What should I do if the website is not loading? Try refreshing the page, clearing your browser cache, or using another browser. Contact support if the problem continues.",

    "What should I do if I cannot log in? Check that your email and password are correct and use the password reset option if necessary.",

    "Why am I not receiving emails? Check your spam or junk folder and verify that your registered email address is correct.",

]


# ============================================================
# REMOVE EXISTING DATA
# ============================================================

print("Checking existing dataset...")

existing = collection.get()

existing_ids = existing.get(
    "ids",
    []
)

if existing_ids:

    print(
        f"Removing {len(existing_ids)} existing FAQ entries..."
    )

    collection.delete(
        ids=existing_ids
    )


# ============================================================
# CREATE UNIQUE IDS
# ============================================================

ids = [
    f"faq_{i}"
    for i in range(len(sample_faq))
]


# ============================================================
# INSERT DATA
# ============================================================

print(
    f"Adding {len(sample_faq)} FAQ entries..."
)

collection.add(
    documents=sample_faq,
    ids=ids
)


# ============================================================
# VERIFY DATA
# ============================================================

final_count = collection.count()


# ============================================================
# SUCCESS MESSAGE
# ============================================================

print("")
print("========================================")
print("Dataset initialization complete")
print("========================================")
print(f"FAQs loaded: {final_count}")
print(f"Database location: {DB_PATH}")
print("========================================")