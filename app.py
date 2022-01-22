import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import os
import threading
import sys

# uncomment line below when running pyinstaller
# os.chdir(sys._MEIPASS)

# Fetch the service account key JSON file contents
cred = credentials.Certificate(
    'firebase-sdk.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://pcshutdown-7d3fb-default-rtdb.firebaseio.com/'
})

db = firestore.client()
# whenever this program runs that means the PC is on
doc_pc_state_ref = db.collection(u'shutdown').document(u'pc_state')
doc_pc_state_ref.update(
    {"state": 1})
# make sure the state is set to 1 because the PC just started
print("PC started")
print("Setting PC state to 1")
if doc_pc_state_ref.get().to_dict()["state"] == 1:
    print("PC state set to 1")
else:
    print("Unable to set PC state to 1")
    exit()

# Create an Event for notifying main thread.
callback_done = threading.Event()


# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        # print(f'Received document snapshot: {doc.id} {doc.to_dict()}')
        if doc.get("state") == 0:
            print("Received shutdown signal | update shutdown time")
            # date time and shutdown pc
            db.collection(u'shutdown').document(u'timestamp').update(
                {"timestamp": datetime.utcnow()})
            callback_done.set()
            callback_done.clear()


# Watch the document
watch_doc = doc_pc_state_ref.on_snapshot(on_snapshot)
callback_done.wait()
print("shutting down pc")
os.system("shutdown /s /t 10")
