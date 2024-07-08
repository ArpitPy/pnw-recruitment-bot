

import time
import json
import requests
from requests.exceptions import ConnectionError
import traceback

__version__ = "2.0.1"
__author__ = "Mountain Dew#0933"
__description__ = "A Python recruiter for Politics and War"


def get_inputs():
    usrnme = input("Please enter your Politics and War login email!\n")
    psswrd = input("Please enter your Politics and War login password!\n")
    apikey = input("Please enter your Politics and War api key!\n")

    try:
        mincit = input("Please enter lowest city amount you will accept! "
                       "If you don't wish to set a limit, just press enter.\n")
        mincit = int(mincit) if mincit and int(mincit) >= 0 else 0
    except ValueError:
        mincit = 0

    try:
        sndtaa = input("Please enter an alliance ID to be targeted by this recruiter. "
                       "If you don't wish to target an alliance, just press enter.\n")
        sndtaa = int(sndtaa) if sndtaa and int(sndtaa) >= 0 else 0
    except ValueError:
        sndtaa = 0

    save_inputs(usrnme, psswrd, apikey, mincit, sndtaa)


def save_inputs(usrnme, psswrd, apikey, mincit, sndtaa):
    data = {"lgusr": usrnme, "lgpsw": psswrd, "apiky": apikey, "mncit": mincit, "tgtaa": sndtaa}

    with open("credentials.json", "w") as result:
        json.dump(data, result)


def get_credentials():
    while True:
        try:
            with open('credentials.json') as result:
                crds = json.load(result)
                return crds["lgusr"], crds["lgpsw"], crds["apiky"], int(crds["mncit"]), int(crds["tgtaa"])
        except (FileNotFoundError, KeyError, ValueError):
            get_inputs()


def get_message():
    files = {"subject": "subject.txt", "message": "message.txt"}
    done = []
    for part, file in files.items():
        while True:
            try:
                with open(file) as result:
                    out = result.read()
                    if len(out) == 0 or out == f"Replace This Text With Your {part.title()}!":
                        input(f"Please take this time to fill out the {file} file in the recruiter folder!\n"
                              f"This is the {part} I will send to players in game as your recruitment {part}!\n"
                              "Press enter when you're ready!")
                        out = None

            except FileNotFoundError:
                out = None
                with open(file, "w") as result:
                    result.write(f"Replace This Text With Your {part.title()}!")

            if out:
                done.append(out)
                break

    return done[0], done[1]


def get_sent():
    try:
        with open("tracker.json", "r+") as sent:
            sent_to = json.load(sent)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        sent_to = []
        with open("tracker.json", "w") as sent:
            json.dump(sent_to, sent)
    return sent_to


def set_sent(sent_to):
    try:
        with open('tracker.json', 'w') as sent:
            json.dump(sent_to, sent)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        with open("tracker.json", "w") as sent:
            json.dump(sent_to, sent)
    print("Tracker Updated")


def get_nations(api_key):
    try:
        nations_api = f'https://politicsandwar.com/api/nations/?key={api_key}'
        nations_data = requests.get(nations_api).json()
        return nations_data["nations"]
    except json.decoder.JSONDecodeError:
        print("JSON Decode Error while connecting to the nations api! The recruiter will try again later...")
    except ConnectionError:
        print("Connection Error while connecting to the nations api! "
              "Is the server down? The recruiter will try again later...")
    except KeyError:
        print("There was a problem with the given api key! Are you out of api calls? "
              "The recruiter will try again later...")
    except:
        print("There was an issue connecting to the api! The recruiter will try again later...")
    return None


def runner():
    print("PnW Recruiter - Free - Python Edition")
    print(f"Version {__version__}")
    print("Developed by the Requiem Project Team")

    runs = 0
    while True:
        try:
            runs += 1
            print(f"The Recruiter has started run {runs}!")
            start = time.time()
            run()
            end = time.time()
            print(f"The Recruiter has completed run {runs} in {int(end-start)} seconds!")
        except Exception as error:
            error = error.__cause__ or error
            tb = traceback.format_exception(type(error), error, error.__traceback__, chain=False)
            tb = "".join(tb)
            print(f"Unhandled Critical Exception:\n{tb}")
        time.sleep(900)


def run():
    lgusr, lgpsw, apiky, mncit, tgtaa = get_credentials()
    print("Credentials Retrieved")
    sub, msg = get_message()
    print("Message and Subject Retrieved")
    print("Retrieving Nations Data")
    nations_data = get_nations(apiky)
    if nations_data:
        print("Nations Data Retrieved")

        with requests.Session() as s:
            sent = 0
            sent_to = get_sent()
            
            for nation in nations_data:
                if all(i for i in (nation['cities'] >= mncit,
                                    nation['allianceid'] == tgtaa,
                                    int(nation['minutessinceactive']) < 1440,
                                    int(nation['nationid']) not in sent_to,
                                    int(nation['nationid']) != 6)):

                    sent += 1
                    receiver = nation['nationid']
                    message_data = {
                        "to": receiver,
                        "subject": sub,
                        "message": msg.replace("%leader%", nation["leader"]).replace("%nation%", nation["nation"])
                    }
                    sendResult = s.post("https://politicsandwar.com/api/send-message/?key=" + apiky, data=message_data)
                    print(f'Message #{sent} Sent to: {nation["leader"]} Nation ID: {nation["nationid"]} | {sendResult}')
                    sent_to.append(nation["nationid"])

                if nation["nationid"] in sent_to and nation["allianceid"] != tgtaa:
                    sent_to.remove(nation["nationid"])

                set_sent(sent_to)

    else:
        print("Failed to Retrieve Nations Data")


runner()
