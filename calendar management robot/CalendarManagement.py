from datetime import datetime
import sqlite3
import cosineSimularity
import textTokenize
import tf_idf
import re

# the intents for calendar management system(use for calender_intent_matching)
intents = {
    "view_schedule": ["Please show me", "view", "take a look", "report", "open", "display", "check", "see"],
    "add_event": ["add", "create", "arrange Schedule", "insert", "set", "book", "plan"],
    "delete_event": ["Delete", "cancel", "remove", "discard", "withdraw", "erase"],
    "negative": ["No", "don't", "not"],
}
conn = sqlite3.connect("calender.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        date TEXT,
        start_time TEXT,
        end_time TEXT,
        event TEXT
    )
''')
user_name = ""  # global variable to store the user's name

'''
This function is used to interactive with database and add event to the table in calendar

Parameters:
- date: The date of the event
- start_time: start time of event
- end_time: end time of the event
- event: The event title

Returns:
print different messages for different event(wrong events and the events that could be stored)
'''


def add_event_to_db(date, start_time, end_time, event):
    global user_name

    # Retrieve existing events from the database for the given date
    cursor.execute("SELECT start_time, end_time, event FROM events WHERE date=?", (date,))
    existing_events = cursor.fetchall()
    existing_event_title = ""
    # Check if there are any existing events for the given date
    if existing_events:
        # Iterate through each existing event
        for existing_event in existing_events:
            # Convert existing and new event times to datetime objects
            existing_start_time = datetime.strptime(existing_event[0], "%H:%M")
            existing_end_time = datetime.strptime(existing_event[1], "%H:%M")
            existing_event_title = existing_event[2]
            new_start_time = datetime.strptime(start_time, "%H:%M")
            new_end_time = datetime.strptime(end_time, "%H:%M")

            # Check if the new event's start time is greater than its end time(avoid wrong event input)
            if new_start_time > new_end_time:
                print("Looks like the end time is bigger the start time."
                      " I can not do this for you, please try to add another event.")
                return

            # Check for event conflicts with existing events
            if existing_start_time <= new_end_time and existing_end_time >= new_start_time:
                print(f"I see there's an event conflict with {existing_event_title}, Do you wish me to continue?(Y/N)")
                while True:
                    user_input = input(f"{user_name}: ")
                    if user_input == "Y":
                        break
                    elif user_input == "N":
                        print("OK. I won't add this event to your calendar.")
                        return
                    else:
                        print("Please type 'Y' or 'N' to continue the conversation.")

    # Insert new event into database
    cursor.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (date, start_time, end_time, event))
    conn.commit()
    print("The new event has been added!")


'''
This function is used to view the event in a specific day

Parameter
- date: The date user want to preview the schedule on

Return
True for correct type of date
False for not correct type date(date not exist etc.)
'''


def view_schedule_from_db(date):
    try:
        today = datetime.strptime(date, '%Y-%m-%d')

        cursor.execute("SELECT start_time, end_time, event FROM events WHERE date=?", (date,))
        events = cursor.fetchall()

        if events:
            events.sort(key=lambda x: datetime.strptime(x[0], "%H:%M"))
            print(f"Your schedule in {date}")  # Print the schedule for the given date
            for event in events:
                start_time = datetime.strptime(event[0], "%H:%M").strftime("%I:%M %p")
                end_time = datetime.strptime(event[1], "%H:%M").strftime("%I:%M %p")
                event_name = event[2]
                print(f"{start_time} - {end_time}: {event_name}")
        else:
            print("Free! Enjoy your day.")  # If no events, print a message indicating a free day
        return True
    except ValueError:
        print("Sorry, I can't identify your format, please try again or quit current process(YYYY-MM-DD)")
        return False # Return False to indicate a date that not exist


'''
This function is to delete the event that the user wish to delete from database

Parameter:
- date: date for the event that user wish to delete 
- event: event title

Return:
print different messages for different user input
'''


def delete_event_from_db(date, event):
    try:
        cursor.execute("DELETE FROM events WHERE date=? AND event=?", (date, event))
        conn.commit()
        print("Successfully deleted event")
    except Exception:
        print(f"Sorry,seems like no {event} in your schedule")


'''
test_quit is used to test whether the user want to exist current conversation

Parameter:
- user_input: user input message

Return:
True if the user want to exit current process
False if the user have other intent
'''


def test_quit(user_input):
    if user_input.lower() == "exit" or user_input.lower() == "quit":
        print("I have quit current process. Thank you for using management system.")
        return True
    else:
        return False


'''
This function is to test whether the user have negative feeling or not happy with current conversation

Parameter:
- user_input: User input message

Return:
True for user have negative feedback
False for no negative feedback detected
'''


def test_negative(user_input):
    tokenized_userinput = textTokenize.tokenize_sentence(user_input)
    action = calender_intent_matching(tokenized_userinput)
    if action == 'negative':
        return True
    else:
        return False


'''
calender_intent_matching is used for analysis the user intent for management system
The function will match the user intent to a specific intent in calendar management system

Parameter:
- tokenized_userinput: Preprocessed user 

Return:
The matched intent
'''


def calender_intent_matching(tokenized_userinput):
    max_similarity = -1
    matched_intent = None

    # use tf to weight the user input and the example intent
    for intent, examples in intents.items():
        query_tf = tf_idf.compute_tf(tokenized_userinput)
        for example in examples:
            preprocessed_example = textTokenize.tokenize_sentence(example)
            tf = tf_idf.compute_tf(preprocessed_example)
            similarity = cosineSimularity.compute_cosine_similarity(query_tf, tf)

            if similarity > max_similarity:
                max_similarity = similarity
                matched_intent = intent

    return matched_intent


'''
detect whether the user input the correct format

Parameter:
- input_string: date massage from user

Return:
None for wrong date format
date_str(date in string format) for correct date format(YYYY-MM-DD) 
'''


def detect_date(input_string):
    pattern = r"\d{4}-\d{2}-\d{2}"  # Regular expression pattern
    match = re.search(pattern, input_string)  # Search for matches in the input string

    if match:
        date_str = match.group()
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            return None
    else:
        return None  # No date found


def detect_time(input_string):
    pattern = r"\d{2}:\d{2}"
    match = re.search(pattern, input_string)
    if match:
        time_str = match.group()
        hour, minute = map(int, time_str.split(':'))

        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return None
        return time_str
    else:
        return None


def greeting_message():
    print("Hello! I'm here to assist you with your event management.")
    print("I can help you find a schedule for a specific date or add "
          "or remove a schedule for a particular day.")


'''
The main loop for calendar management system
Accept user input then match it to specific intent, finally output the action that match the user intent

Parameter:
- username: The user name for current user
- siginal: Whether it's the first time for the user to use the calendar management system
- user_input: The input message from main function

Return:
complete the action 
return 0 for exit the system
return 1 for exit current process
return 2 for success complete the conversation
'''


def main_loop(username, siginal, user_input):
    # if siginal:
    #     greeting_message()
    global user_name
    user_name = username

    if user_input.lower() == "exit" or user_input.lower() == "quit":
        return 0
    tokenized_userinput = textTokenize.tokenize_sentence(user_input)
    action = calender_intent_matching(tokenized_userinput)
    # view schedule action, the chatbot will ask for date, then it could handle "quit", error format etc. Fail three
    # times will lead to "quit"
    if action == "view_schedule":
        counter = 0
        print("Sure! I can help you with that! ")
        print("Could you please provide the detailed information about the date? (YYYY-MM-DD)")
        while counter < 3:
            date = input(f"{username}: ")
            if test_quit(date):
                break
            date = detect_date(date)
            if date != None:
                check = view_schedule_from_db(date)
                if check:
                    break
                else:
                    counter += 1
            else:
                counter += 1
                print("I'm sorry, I can't detect valid date(YYYY-MM-DD), could you please try again?")
        if counter >= 3:
            print("Sorry, it seems that I am unable to fulfill your request. Please change a job for me")
            return 1
        return 2
    elif action == "add_event":
        print("I see you are trying to add an event to your calender, could you please tell me the event title")
        event = input(f"{username}: ")
        if test_quit(event):
            return 1

        print("Thank you! Could you please tell me the detailed date for this event? (yyyy-mm-dd)")
        counter = 0
        while counter < 3:
            date = input(f"{username}: ")
            if test_quit(date):
                return 1
            date = detect_date(date)
            if date == None:
                counter += 1
                print("I'm sorry, I can't detect valid date(YYYY-MM-DD), could you please try again?")
            else:
                break
        if counter >= 3:
            print("Sorry, it seems that I am unable to fulfill your request. Please change a job for me")
            return 1

        print("When will this event start? (HH:MM)")
        counter = 0
        while counter < 3:
            start_time = input(f"{username}: ")
            if test_quit(start_time):
                return 1
            start_time = detect_time(start_time)
            if start_time == None:
                counter += 1
                print("I'm sorry, I can't detect valid start time(HH:MM), could you please try again?")
            else:
                break
        if counter >= 3:
            print("Sorry, it seems that I am unable to fulfill your request. Please change a job for me")
            return 1

        print("One step further, the end time, please? (HH:MM)")
        counter = 0
        while counter < 3:
            end_time = input(f"{username}: ")
            if test_quit(end_time):
                return 1
            end_time = detect_time(end_time)
            if end_time == None:
                counter += 1
                print("I'm sorry, I can't detect valid start time(HH:MM), could you please try again?")
            else:
                break
        if counter >= 3:
            print("Sorry, it seems that I am unable to fulfill your request. Please change a job for me")
            return 1

        add_event_to_db(date, start_time, end_time, event)
        view_schedule_from_db(date)
        return 2
    elif action == "delete_event":
        print("Please enter the date(yyyy-mm-dd)")
        date = input(f"{username}: ")

        print("Please enter the event that you want to delete")
        event = input(f"{username}: ")

        delete_event_from_db(date, event)
        return 2
    else:
        print("I'm sorry, could you provide a more specific instruction?")
