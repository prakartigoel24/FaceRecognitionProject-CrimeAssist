# FaceRecognitionProject - Crime Assist


This is a Web based App integrated with the Facial-Recognition Technology.

This App focuses on storing, manipulating and searching Convict Records in the Database with the help of Face Recognition to identify and get the details of convicts.

*Download and open the **RecordedSteps** file to see the App demo as screenshots.*

*Checkout the [**VideoDemo**](https://youtu.be/PITixMA5UqU) link to see the video demo of this App.*

## Features of this Web-App

            -> Registration using Email and Password

            -> Login using Email and Password
         
            -> * Face Login * 

            -> Adding Convicts to Database
            
            -> Updating Convict records in Database
            
            -> Deleting Convict records from Database
            
            -> Searching the Database using Convict details
            
            -> * Identifying the Convict using Images *
            
            -> * Identifying the Convict using Video *


## Overview of the Tech-Stack used :

- **Languages**  : Python, Html, Css
- **Framework** : Flask
- **Libraries** : Face-Recognition, OpenCV, Pillow
- **Database toolkit** : SQLAlchemy
- **Database** : SQLite


# Steps To Run This Project On Your Device : #

-> **For installing Face-Recognition library on Mac or Linux :**  
            
 - Install dlib with Python bindings [refer this link]( https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)
 - Then, make sure you have cmake installed: `brew install cmake`

 - Finally, install this module from pypi using pip3 (or pip2 for Python 2): `pip3 install face_recognition`
  
  
 -> **For Running on Windows follow the steps below -**  

1. Install python-3.8 (64 bit) or above from 'https://www.python.org/downloads/' and add the PATH to your USER and System Variables under Environment variables. 

2. Install VISUAL STUDIO Community Edition  from 'https://visualstudio.microsoft.com/downloads/' and install plugins for PYTHON development and C++ Desktop Development (important).

3. Install VsCode or any other IDE of your choice on your device and make sure to check the add to PATH checkbox.

4. Clone this repository on your system using `git clone <repo url>` command. 

5. Open the project folder in your IDE .

6. Install cmake using `pip install cmake` and then install dlib using `pip install dlib`, after these install the other required packages from the 'requirements.txt' file by running the `pip install -r requirements.txt` command on your IDE's terminal.
            
7. Run the python file named - **`run.py`**

8. Click on the link which shows up on the terminal or type **localhost:5000** on your browser.

9. Now you're all set to try the Web-Application on your device! Woohooo!

### Important ###
  - Set your own secret key for the web-app if you like.
  - If there is an error like - SMTPAuthenticationError while sending mail for Password Reset , kindly go to the - *setting/security/lesssecureapps* of your Google account which you have used to send mail and enable access to less secure apps.

---


*All critics and suggestions to improve this Web-App are always whole-heartedly welcome! ????*



