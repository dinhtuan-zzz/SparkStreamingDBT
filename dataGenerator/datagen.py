import faker
import random
import datetime
import json

# Create a faker instance
fake = faker.Faker()


def generate_data():
    """Generates random data in the specified format"""
    data = {}
    # Generate numeric id
    data["id"] = random.randint(1000, 9999)
    # Generate uuid
    data["uid"] = fake.uuid4()
    # Generate password
    data["password"] = fake.password()
    # Generate first and last names
    data["first_name"] = fake.first_name()
    data["last_name"] = fake.last_name()
    # Generate username
    data["username"] = data["first_name"] + "." + data["last_name"].lower()
    # Generate email
    data["email"] = data["username"] + "@email.com"
    # Generate avatar url using faker image url
    data["avatar"] = fake.image_url()
    # Randomly choose gender
    data["gender"] = random.choice(["Male", "Female", "Non-binary"])
    # Generate phone number
    data["phone_number"] = fake.phone_number()
    # Generate social security number (replace with any other identifier if needed)
    data["social_insurance_number"] = "".join([str(random.randint(0, 9)) for _ in range(9)])
    # Generate date of birth
    data["date_of_birth"] = fake.date_of_birth()

    # Generate employment data
    data["employment"] = {}
    data["employment"]["title"] = fake.job().title()


    # Generate address data
    data["address"] = {}
    data["address"]["city"] = fake.city()
    data["address"]["street_name"] = fake.street_name()
    data["address"]["street_address"] = fake.street_address()
    data["address"]["zip_code"] = fake.postcode()
    data["address"]["state"] = fake.state()
    data["address"]["country"] = fake.country()
    # Generate random latitude and longitude within a reasonable range
    data["address"]["coordinates"] = {"lat": random.uniform(20, 50), "lng": random.uniform(-130, -70)}

    # Generate credit card data (replace with any other data if needed)
    data["credit_card"] = {}
    data["credit_card"]["cc_number"] = fake.credit_card_number()

    # Generate subscription data
    data["subscription"] = {}
    data["subscription"]["plan"] = random.choice(["Bronze", "Silver", "Gold"])
    data["subscription"]["status"] = random.choice(["Active", "Inactive"])
    data["subscription"]["payment_method"] = random.choice(["Paypal", "Credit Card", "Direct Debit"])
    data["subscription"]["term"] = random.choice(["Monthly", "Annual"])

    return data


print(type(generate_data()))
