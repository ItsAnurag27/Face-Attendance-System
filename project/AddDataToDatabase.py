import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("#add credential.Certificate file(json file of database")
firebase_admin.initialize_app(cred,{

    'databaseURL':"#Paste database url here",
})



ref=db.reference("Student")
data = {
    "911890":
        {
            "name":"Anurag Gupta",
            "dob":"27-08-2005",
            "branch":"B-Tech",
            "total_attendance":6,
            "last_attendance_time": "2024-05-02  00:45:30",
        },
    "945415":
        {
            "name":"elon musk ",
            "dob":"27-08-1990",
            "branch":"B-Tech",
            "total_attendance":16,
            "last_attendance_time": "2024-05-02  00:45:30",
        },
    "7080599":
        {
            "name":"bill gates",
            "dob":"27-08-1960",
            "branch":"B-Tech",
            "total_attendance":15,
            "last_attendance_time": "2024-05-02  00:45:30",
        }

}
for key,value in data.items():
    ref.child(key).set(value)

