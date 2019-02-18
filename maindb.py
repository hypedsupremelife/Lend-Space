import requests, json, time, datetime, random, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase import firebase

global FirebaseURL
global PasswordString
FirebaseURL = 'https://lendaspacev2.firebaseio.com/'
LotIDString = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

#Go Through Users
def GetData():
    Firebase = firebase.FirebaseApplication(FirebaseURL, None)
    UsersData = Firebase.get('/Users', None)
    arr = []
    for key,value in UsersData.items():
        UserFullName, UserPhone, xd = IterateData(key, Firebase)
        tmp = [UserFullName, UserPhone, xd]
        arr.append(tmp)

    return arr

#Get All Data From Specific User
def IterateData(UserName, Firebase):
    CurrentUser = Firebase.get('/Users', f'{str(UserName)}')
    UserInfo = CurrentUser['UserInfo']

    UserFullName = UserInfo['name']
    UserPhone = UserInfo['phone']
    
    arr = []
    try:
        UserParking = CurrentUser['UserParking']

        arr = []
        for CurrentLot,v in UserParking.items():
            LotLocation = v.get('address')
            LotCount = v['count']
            LotImage = v['imageURL']
            LotName = v['lotname']
            LotPPH = v['pricing']
            LotTimeStart = v['time-start']
            LotTimeEnd = v['time-end']
            tmp = [CurrentLot, LotLocation, LotCount, LotImage, LotName, LotPPH, LotTimeStart, LotTimeEnd]
            arr.append(tmp)
    except:
        pass
    
    return UserFullName, UserPhone, arr

#Add User To Database
def RegisterUser(UserName, UserFullName, UserEmail, UserPassword, UserPhone):
    Firebase = firebase.FirebaseApplication(FirebaseURL, None)
    UserExist, Firebase = CheckUser(UserName)
    if UserExist == True:
        print("Username Unavailable")
        return False
    else:
        print("Username Available")
        UserData = {
            "UserInfo": {
                "email": UserEmail,
                "name": UserFullName,
                "password": UserPassword,
                "phone": UserPhone
            }
        }  
        Firebase.put(f'Users', UserName, UserData)
        return True

#Add A Lot
def AddLot(UserName, LotLocation, LotCount, LotImage, LotName, LotPPH, LotTimeEnd, LotTimeStart):
    LotID = ""
    for x in range(24):
        Letter = random.choice(LotIDString)
        LotID = LotID + Letter

    Firebase = firebase.FirebaseApplication(FirebaseURL, None)
    LotData = {
        "address": LotLocation,
        "count": int(LotCount),
        "imageURL": LotImage,
        "lotname": LotName,
        "pricing": int(LotPPH),
        "time-end": LotTimeEnd,
        "time-start": LotTimeStart
    }
    Firebase.put(f'Users/{str(UserName)}/UserParking', LotID, LotData)

#Check If User Exists In DB (REGISTER + LOGIN)
def CheckUser(UserName):
    Firebase = firebase.FirebaseApplication(FirebaseURL, None)
    UsersData = Firebase.get('/Users', None)

    for User in UsersData:
        if UserName == User:
            return True, Firebase
        else:
            pass
    return False, Firebase

#Login User Through Site
def LoginUser(UserName, PasswordEntered):
    UserExist, Firebase = CheckUser(UserName)
    if UserExist:
        CurrentUser = Firebase.get('/Users', f'{str(UserName)}')
        UserPassword = CurrentUser['UserInfo']['password']

        if UserPassword == PasswordEntered:
            return True
        else:
            print("Incorrect Username or Password")
            return False

    else:
        print("Incorrect Username or Password")
        return False

#Remove Lot On Sale Or Removal
def RemoveLot(User, LotID):
    Firebase = firebase.FirebaseApplication(FirebaseURL, None)
    UsersData = Firebase.get('/Users', None)
    for User in UsersData:
        ParkingSpotData = Firebase.get(f"Users/{str(User)}/UserParking", None)
        for Spot in ParkingSpotData:
            if Spot == LotID:
                ParkingSPotData = Firebase.get(f"Users/{str(User)}/UserParking", LotID)
                UserData = Firebase.get(f"Users/{User}", "UserInfo")
                CustomerName = UserData['name']
                CustomerEmail = UserData['email']
                SendEmail(CustomerEmail, CustomerName, ParkingSPotData, UserData)
                Firebase.delete(f"Users/{str(User)}/UserParking", LotID)

#Send Purchase Email
def SendEmail(CustomerEmail, CustomerName, ParkingSPotData, UserData):
    sender_email = "LendASpacePurchase@gmail.com"
    password = "AdminLogin22"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Update From Lend-A-Space"
    message["From"] = sender_email
    message["To"] = CustomerEmail

    html = f"""\
    <html>
    <body>
        <p>Hi, {str(CustomerName)}<br>
        <p><b>Contact name:</b> {str(UserData['name'])}<br>
            <b>Contact phone:</b> {str(UserData['phone'])}<br>
            <b>Contact email:</b> {str(UserData['email'])}<br>
            <b>Lot address:</b><a href="{"https://google.com/maps/place/"+ParkingSPotData['address'].replace(" ", "+")}"> {ParkingSPotData['address']}</a><br>
            <b>Lot capacity:</b> {ParkingSPotData['count']}<br>
            <b>Lot pricing:</b> {ParkingSPotData['pricing']}<br>
            <b>Rent start time:</b> {ParkingSPotData['time-start']}<br>
            <b>Rent end time:</b> {ParkingSPotData['time-end']}
        </p>
        </p>
    </body>
    </html>
    """

    part1 = MIMEText(html, "html")
    message.attach(part1)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email,
            CustomerEmail,
            message.as_string(),
        )

#Get Users Current Lots -- For Account Dashboard
def GetUserLots(UserName):
    Firebase = firebase.FirebaseApplication(FirebaseURL, None)
    CurrentUser = Firebase.get('/Users', f'{str(UserName)}')
    UserInfo = CurrentUser['UserInfo']
    UserParking = CurrentUser['UserParking']

    UserEmail = UserInfo['email']
    UserFullName = UserInfo['name']
    UserPhone = UserInfo['phone']

    arr = []
    for CurrentLot,v in UserParking.items():
        LotLocation = v['address']
        LotCount = v['count']
        LotImage = v['imageURL']
        LotName = v['lotname']
        LotPPH = v['pricing']
        LotTimeStart = v['time-start']
        LotTimeEnd = v['time-end']
        tmp = [CurrentLot, LotLocation, LotCount, LotImage, LotName, LotPPH, LotTimeStart, LotTimeEnd]
        arr.append(tmp)
    
    return UserFullName, UserPhone, UserEmail, arr