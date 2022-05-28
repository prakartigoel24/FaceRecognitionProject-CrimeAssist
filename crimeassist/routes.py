from calendar import c
from fileinput import filename
import cv2
from werkzeug.utils import secure_filename
import numpy as np
import os, time
from datetime import date
from flask_table import Table, Col
import secrets
from PIL import Image,ImageDraw,ImageFont
import email
import face_recognition
from flask import Flask, flash,request, Response
from flask import redirect,url_for,render_template,request
from crimeassist import app,db,bcrypt, mail
from crimeassist.forms import*
from crimeassist.models import*
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message


user_face_encodings = []
user_ids = []
convict_face_encodings = []
convict_ids = []
convict_names= []

def generate_user_setup_encoding():
    user_face_encodings.clear()
    user_ids.clear()
    folder = "D:\Flask\crimeassist\static\profile_pics"
    list_of_images = os.listdir(folder)

    for imgName in list_of_images:
        currImg = face_recognition.load_image_file(f'{folder}\{imgName}')
        new_id = imgName.split('.')
        img = cv2.cvtColor(currImg, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img)
        if face_locations:
            currImgEncodings = face_recognition.face_encodings(img, face_locations)[0]
            user_face_encodings.append(currImgEncodings)
            user_ids.append(new_id[0])
    print(user_ids)

def generate_convict_encodings():
    convict_face_encodings.clear()
    convict_ids.clear()
    convict_names.clear()
    folder = "D:\Flask\crimeassist\static\convict_pics"
    list_of_images = os.listdir(folder)
    convicts = Convict.query.all()

    for con in convicts:
        curr_con_id = con.id
        curr_con_img =con.profile_image
        currImg = face_recognition.load_image_file(f'{folder}\{curr_con_img}')
        img = cv2.cvtColor(currImg, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img)
        if face_locations:       
            currImgEncodings = face_recognition.face_encodings(img)[0]
            convict_face_encodings.append(currImgEncodings)
            convict_ids.append(curr_con_id)
            convict_names.append(con.name)
    print(convict_ids)
    print(convict_names)
    print(len(convict_face_encodings))


generate_user_setup_encoding()
generate_convict_encodings()

def generate_img(cam, label, foldername):
    while True:
        # Grab a single frame of video
        success, frame = cam.read()

        if not success:
            print("oops ! something went wrong")
            break
        else:
            output_size = (125,125)
            imgname = str(label) + '.jpg'
            path = os.path.join('crimeassist\static',foldername)
            path = os.path.join(path, imgname)
            cv2.imwrite(path, frame)
            ret, imgbuffer = cv2.imencode('.jpg',frame)
            frame=imgbuffer.tobytes()
            
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_convict_img(cam,foldername,imghex):
    while True:
        # Grab a single frame of video
        success, frame = cam.read()

        if not success:
            print("oops ! something went wrong")
            break
        else:
            imgname = str(imghex) + '.jpg'
            path = os.path.join('crimeassist\static',foldername)
            path = os.path.join(path, imgname)
            cv2.imwrite(path, frame)
            ret, imgbuffer = cv2.imencode('.jpg',frame)
            frame=imgbuffer.tobytes()
            
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
     
    
@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form  = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember = form.remember.data)
            next_page = request.args.get('next')            
            flash('login succesful!','success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('login unsuccesful! Please check email and password.','danger')
    return  render_template('login.html' , form=form , title='Login Form')

@app.route('/face_login_setup', methods=['POST', 'GET'])
@login_required
def face_login_setup():
    id = current_user.id
    user_img = str(id) + '.jpg'
    current_user.image_file = user_img
    db.session.commit()
    return render_template('face_login_setup.html')

@app.route('/video_feed', methods=['POST', 'GET'])
@login_required
def video_feed():
    cam = cv2.VideoCapture(0)
    return Response(generate_img(cam, current_user.id,foldername='profile_pics'), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stop', methods=['POST', 'GET'])
@login_required
def stop():
    generate_user_setup_encoding()
    flash('Image successfully captured! You can now Login using Face Login.', 'success')
    return redirect(url_for('home'))

@app.route('/video_feed_login/<user_email>', methods=['POST', 'GET'])
def video_feed_login(user_email):
    cam = cv2.VideoCapture(0)
    return Response(generate_img(cam,user_email,foldername='login_user_images'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/goto_facelogin/<user_email>')
def goto_facelogin(user_email):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    return render_template('face_login.html', user_email = user_email)

@app.route('/face_login', methods=['POST', 'GET'])
def face_login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form  = FaceLoginForm()
    if form.validate_on_submit():  
        user_email = form.email.data
        user = User.query.filter_by(email=user_email).first()
        if user:
            if user.image_file:
                return redirect(url_for('goto_facelogin', user_email= str(user_email))) 
            else:
                flash('Face Login is not Set-up', 'info')
        else:
            flash('User does not exist with that email!', 'danger')
    return render_template('emailpage.html', form=form)

@app.route('/try_face_login/<user_email>')
def try_face_login(user_email):
    tryimageloc =f'crimeassist\static\login_user_images\{user_email}.jpg' 
    currImg = face_recognition.load_image_file(tryimageloc)
    img = cv2.cvtColor(currImg, cv2.COLOR_BGR2RGB) 
    face_locations = face_recognition.face_locations(img)
    if face_locations:
        currImgEncodings = face_recognition.face_encodings(img, face_locations)
    else:
        flash(' Face not detected ! Try again.', 'info')
        return redirect(url_for('face_login'))

    for face_encoding in currImgEncodings:
        matches = face_recognition.compare_faces(user_face_encodings, face_encoding,tolerance=0.6)
        face_distances = face_recognition.face_distance(user_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            id = user_ids[best_match_index]
            user = User.query.filter_by(id = id).first()
            if user.email == user_email:
                login_user(user,remember = True)
                flash('Login successful!','success')
                return redirect(url_for('home'))
            else:
                flash('Face match invalid, please login through Email and pass', 'info')
                return redirect(url_for('login'))
        else:
            flash('Invalid face login. Please login through Email and pass', 'info')
            return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form  = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data,email=form.email.data,password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data} ! You can now Log In', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html' , form=form,title='Registration Form')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/logout')
def logout(): 
    logout_user()
    return redirect(url_for('home'))

def save_convict_picture(form_picture, imghex):
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn= imghex + f_ext
    picture_path = os.path.join(app.root_path,'static/convict_pics', picture_fn)
    output_size = (125,125)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():  
    form =  UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data and form.confirm_password.data:
            if bcrypt.check_password_hash(current_user.password,form.password.data):
                hashed_password = bcrypt.generate_password_hash(form.confirm_password.data).decode('utf-8')
                current_user.password = hashed_password
            else:
                flash('Please check your existing account password!','danger')
                return redirect(url_for('account'))
        elif not form.password.data and not form.confirm_password.data:
            pass
        else:
            flash("Please fill both fields in Update Password.",'info')
            return redirect(url_for('account'))
        
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html',title='Account', form = form)

@app.route('/addConvict', methods=['POST', 'GET'])
@login_required
def addConvict():
    form = AddConvictForm()
    imghex = secrets.token_hex(8)
    picture_file  = str(imghex) + '.jpg'
    if form.validate_on_submit():
        if not form.picture.data:
            flash('Image required!', "danger")
        else:
            save_convict_picture(form.picture.data, imghex)
            newconvict = Convict(name = form.name.data,crimes = form.crimes.data,dob = form.dob.data ,profile_image = picture_file)
            db.session.add(newconvict)
            db.session.commit()
            generate_convict_encodings()
            flash('Convict added successfully!', 'success')  
            return redirect(url_for('showConvicts' , Convict = Convict))  
    return render_template('addConvict.html',title='Add Convict', form = form, imghex=str(imghex))


@app.route('/showConvicts', methods=['POST', 'GET'])
@login_required
def showConvicts():
    page=request.args.get('page',1,type=int)
    convicts = Convict.query.order_by(Convict.name).paginate(page=page,per_page=3)
    return render_template('showConvicts.html',title='Convict List' ,convicts = convicts,Convict = Convict)



@app.route('/updateConvictInfo/<int:convict_id>', methods=['POST', 'GET'])
@login_required
def updateConvictInfo(convict_id):
    imghex = secrets.token_hex(8)
    picture_file  = str(imghex) + '.jpg'
    convict = Convict.query.get_or_404(convict_id)
    form = UpdateConvictForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            save_convict_picture(form.profile_image.data, imghex)
            img = convict.profile_image
            loc = "D:\Flask\crimeassist\static\convict_pics"
            path1 = os.path.join(loc,img)
            os.remove(path1)
            convict.profile_image=picture_file        
        convict.name = form.name.data
        convict.crimes = form.crimes.data
        convict.dob = form.dob.data
        db.session.commit()
        generate_convict_encodings()
        flash('Convict info Updated successfully!','success')
        return redirect(url_for('update'))
    elif request.method == 'GET':
        form.name.data = convict.name
        form.crimes.data  =convict.crimes
        form.dob.data =convict.dob
        form.profile_image.data =convict.profile_image

    return render_template('updateConvictInfo.html',title='Update Info', form=form)

@app.route('/deleteConvict/<int:convict_id>', methods=['POST', 'GET'])
@login_required
def deleteConvict(convict_id):
    convict = Convict.query.get_or_404(convict_id)
    db.session.delete(convict)
    img1 = convict.profile_image
    loc = "D:\Flask\crimeassist\static\convict_pics"
    path1 = os.path.join(loc,img1)
    os.remove(path1)
    generate_convict_encodings()
    db.session.commit() 
    flash('Convict Profile Deleted successfully!','success')
    return redirect(url_for('update'))


@app.route('/searchConvict', methods=['POST', 'GET'])
@login_required
def searchConvict():
    form = SearchForm()
    if request.method == 'POST':
        form_keyword = form.search.data
        form_choice = form.search_using.data
        if form_choice == 'name':
            convicts = Convict.query.filter(Convict.name.contains(form_keyword)).all()        

        elif form_choice == 'dob':
            convicts = Convict.query.filter(Convict.dob.contains(form_keyword)).all()        

        elif form_choice == 'id':
            convicts = Convict.query.filter(Convict.id.contains(form_keyword)).all()        

        elif form_choice == 'crimes':
            convicts = Convict.query.filter(Convict.crimes.contains(form_keyword)).all()        

        return render_template('searchConvict.html',form=form,convicts=convicts)
    return render_template('searchConvict.html',form=form)


def process_img(img):
    convicts = []
    folder = "D:\\Flask\\crimeassist\\static\\uploads"
    currImg = face_recognition.load_image_file(f'{folder}\{img}')
    pil_image = Image.fromarray(currImg)
    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)
    imgrgb = cv2.cvtColor(currImg, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(imgrgb, model='large')
    if face_locations:
        currImgEncodings = face_recognition.face_encodings(imgrgb, face_locations)
        for (top, right, bottom, left), face_encoding in zip(face_locations, currImgEncodings):
            matches = face_recognition.compare_faces(convict_face_encodings, face_encoding, tolerance=0.6)
            name  = 'unknown'
            face_distances = face_recognition.face_distance(convict_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                id = convict_ids[best_match_index]
                con = Convict.query.filter_by(id=id).first()
                name = con.name
                convicts.append(con)
            draw.rectangle(((left-10, top-10), (right+7, bottom+7)), outline=(0, 0, 255))
            font = ImageFont.truetype('arial.ttf', size=20)
            # Draw a label with a name below the face
            text_width, text_height = draw.textsize(name)
            draw.rectangle(((left-10, bottom - text_height+1), (right+6, bottom+15)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height+5 ), name, fill=(255, 255, 255, 255),font = font) 

    del draw
    drawnImage=os.path.join(folder,img)
    pil_image.save(drawnImage)
    return convicts , img

def save_pic(form_picture):
    picture_fn= 'temp.jpg'
    picture_path = os.path.join(app.root_path,'static/uploads', picture_fn)
    i= Image.open(form_picture)
    i.save(picture_path)
    return picture_fn
        
@app.route('/searchUsingMedia', methods=['POST', 'GET'])
@login_required
def searchUsingMedia():
    form = ConvictSearchForm()
    if form.validate_on_submit():
        if form.picture.data:
            i = save_pic(form.picture.data)
            convicts , drawnImage= process_img(i)
            return render_template('searchUsingMedia.html',convicts = convicts, form=form, drawnImage=drawnImage)
                
    return render_template('searchUsingMedia.html', form=form)

@app.route('/update', methods=['POST', 'GET'])
@login_required
def update():
    form = SearchForm()
    convicts=Convict.query.all()
    if request.method == 'POST':
        form_keyword = form.search.data
        form_choice = form.search_using.data
        if form_choice == 'name':
            convicts = Convict.query.filter(Convict.name.contains(form_keyword)).all()        

        elif form_choice == 'dob':
            convicts = Convict.query.filter(Convict.dob.contains(form_keyword)).all()        

        elif form_choice == 'id':
            convicts = Convict.query.filter(Convict.id.contains(form_keyword)).all()        

        elif form_choice == 'crimes':
            convicts = Convict.query.filter(Convict.crimes.contains(form_keyword)).all()      

        return render_template('update.html',form=form,convicts=convicts)


    return render_template('update.html', form=form,convicts=convicts)

def process_vid_gen(vid):
    process_curr_frame=True
    while True:
        # Grab a single frame of video
        success, frame = vid.read()

        if not success:
            print('OOPS SOMETHING WENT WRONG!')
            break
        else:
            # small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = frame[:, :, ::-1]            
            if process_curr_frame:
                # Find all the faces and face encodings in the current frame of video
                vid_face_locations = face_recognition.face_locations(frame)
                vid_face_encodings = face_recognition.face_encodings(rgb_small_frame, vid_face_locations)
                vid_face_names = []

                for face_encoding in vid_face_encodings:
                    # See if the face in video feed is a match for the known faces
                    matches = face_recognition.compare_faces(convict_face_encodings, face_encoding,tolerance=0.6)
                    name = "Unknown"
                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(convict_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = convict_names[best_match_index]
                        
                    vid_face_names.append(name)
            process_curr_frame= not process_curr_frame
            # Display the results
            for (top, right, bottom, left), name in zip(vid_face_locations, vid_face_names):
                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 10), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 4), font, 0.5, (255, 255, 255), 1)

            ret, imgbuffer = cv2.imencode('.jpg',frame)
            frame=imgbuffer.tobytes()
            
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
      f = request.files['file']
      fname = secure_filename("tempVid.mp4")
      f.save(os.path.join('crimeassist/static/uploads',fname))
      flash('Video uploaded!','success')
      vidname =  fname
      return render_template('searchUsingVideo.html', vidname=vidname)
    
    return render_template('searchUsingVideo.html')

@app.route('/process_video/<vidname>', methods = ['GET', 'POST'])
def process_video(vidname):
    vidobj = cv2.VideoCapture(os.path.join('crimeassist/static/uploads',vidname))
    return Response(process_vid_gen(vidobj), mimetype='multipart/x-mixed-replace; boundary=frame')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)