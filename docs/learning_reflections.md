# Learning Reflections: Engineer B

## 1. The history code that crashed my program

When the AI gave me history.py, I thought I was done with that part. The code looked complete and it checked its inputs, so I just plugged it into main.py and tried it.

I ran option 6 to move T001 to in_progress and the program crashed with this:

ValueError: Event has an invalid action.

I was confused because I had never written anything called "action". I checked option 10 for T001 and it said "No history for that ticket", so at least nothing had been saved and my data was fine.

Then I opened storage.py and read validate_events. It wants every event to have ticket_id, action and actor, plus a timestamp with a timezone. My history.py was saving the same value under the name event_type. The AI had never seen storage.py when it wrote my file, so it guessed the name and got it wrong.

What I got wrong was thinking that code which looks right on its own will work in my project. It won't if it disagrees with the file that saves the data. storage.py decides what a valid event is, so history.py has to match it. I did not edit storage.py because it belongs to my teammate and other things depend on it.

I renamed the field in history.py and added a test that passes my events through validate_events. Now if the two files ever disagree again, a test fails first and not the menu. I also give the AI my other files before asking for new code.

## 2. The test that "could not be found"

I wrote test_escalation.py and ran it, and Python said:

ModuleNotFoundError: No module named 'test_escalation'

My first thought was that something was wrong with my escalation code. It wasn't, because the test never even started. I tried the command again and made it worse. I pressed Enter in the middle of it, so the terminal ran "tes" and "t_escalation" as two separate commands.

Then I ran ls test_*.py and got "No such file or directory". After I ran ls and ls tests, I saw two things. My tests are all inside the tests folder, not the main folder. And the file was actually called test_escalaation.py, with two a's.

So the problem was a typo and a wrong folder, not my code. I fixed the name with mv and ran the tests with python -m unittest discover -s tests.

The lesson for me is to check the simple things first. An error message says what Python could not do, but it does not always say why. Looking at the real file names took ten seconds and saved me from changing code that was fine.

## 3. A quiz question I found difficult

I have not done this part yet. After I finish option 11 I will pick one question I missed and write what I first believed, what I checked, and what changed my mind.