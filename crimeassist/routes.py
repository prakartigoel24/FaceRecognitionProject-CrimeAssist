import cv2
import numpy as np
import os, time
from datetime import date
from flask_table import Table, Col
import secrets
from PIL import Image
import email
import face_recognition
from flask import Flask, flash,request, Response
from flask import redirect,url_for,render_template,request
from crimeassist import app,db,bcrypt
from crimeassist.forms import*
from crimeassist.models import*
from flask_login import login_user,current_user,logout_user,login_required

user_face_encodings = []
present_ids = []

def generate_user_setup_encoding():
    folder = "D:\Flask\crimeassist\static\profile_pics"
    list_of_images = os.listdir(folder)

    for imgName in list_of_images:
        currImg = face_recognition.load_image_file(f'{folder}/{imgName}')
        new_id = imgName.split('.')
        present_ids.append(new_id[0])
        img = cv2.cvtColor(currImg, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img)
        if face_locations:
            currImgEncodings = face_recognition.face_encodings(img, face_locations, num_jitters=3, model="large")[0]
            user_face_encodings.append(currImgEncodings)


generate_user_setup_encoding()

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
    return render_template('face_login_setup.html')

@app.route('/video_feed', methods=['POST', 'GET'])
@login_required
def video_feed():
    cam = cv2.VideoCapture(0)
    return Response(generate_img(cam, current_user.id,foldername='profile_pics'), mimetype='multipart/x-mixed-replace; boundary=frame')

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
        return redirect(url_for('goto_facelogin', user_email= str(user_email))) 
    
    return render_template('emailpage.html', form=form)

@app.route('/try_face_login/<user_email>')
def try_face_login(user_email):
    tryimageloc =f'crimeassist\static\login_user_images\{user_email}.jpg' 
    currImg = face_recognition.load_image_file(tryimageloc)
    img = cv2.cvtColor(currImg, cv2.COLOR_BGR2RGB) 
    face_locations = face_recognition.face_locations(img)
    if face_locations:
        currImgEncodings = face_recognition.face_encodings(img, face_locations, num_jitters=3, model="large")
    else:
        flash(' Face not detected ! Try again.', 'info')
        return redirect(url_for('face_login'))

    for face_encoding in currImgEncodings:
        matches = face_recognition.compare_faces(user_face_encodings, face_encoding,tolerance=0.3)
        face_distances = face_recognition.face_distance(user_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            id = present_ids[best_match_index]
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


@app.route('/stop', methods=['POST', 'GET'])
@login_required
def stop():
    flash('Image successfully captured! You can now Login using Face Login.', 'success')
    return redirect(url_for('home'))

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
    
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn= random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics', picture_fn)
    output_size = (125,125)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def save_convict_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn= random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/convict_pics', picture_fn)
    output_size = (125,125)
    i= Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():  
    form =  UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file  = save_picture(form.picture.data)
            img = current_user.image_file
            current_user.image_file  = picture_file
            loc = "D:\Flask\crimeassist\static\profile_pics"
            path1 = os.path.join(loc,img)
            os.remove(path1)
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
    image_file = url_for('static', filename = 'profile_pics/'+ current_user.image_file)
    return render_template('account.html',title='Account', image_file=image_file , form = form)

@app.route('/addConvict', methods=['POST', 'GET'])
@login_required
def addConvict():
    form = AddConvictForm()
    if form.validate_on_submit():
        if not form.picture.data:
            flash("Image file required!", 'danger')
        else:
            picture_file  = save_convict_picture(form.picture.data)
            newconvict = Convict(name = form.name.data,crimes = form.crimes.data,dob = form.dob.data ,profile_image = picture_file)
            db.session.add(newconvict)
            db.session.commit()
            convImg = ConvictImage(person=newconvict,image_file=picture_file)
            db.session.add(convImg)
            db.session.commit()
            flash('Convict added successfully!', 'success')  
            return redirect(url_for('showConvicts' , Convict = Convict))  
    return render_template('addConvict.html',title='Add Convict', form = form)



@app.route('/showConvicts', methods=['POST', 'GET'])
@login_required
def showConvicts():
    page=request.args.get('page',1,type=int)
    convicts = Convict.query.order_by(Convict.name).paginate(page=page,per_page=3)
    return render_template('showConvicts.html',title='Convict List' ,convicts = convicts,Convict = Convict)



@app.route('/updateConvictInfo/<int:convict_id>', methods=['POST', 'GET'])
@login_required
def updateConvictInfo(convict_id):
    convict = Convict.query.get_or_404(convict_id)
    form = UpdateConvictForm()
    if form.validate_on_submit():
        if form.profile_image.data:
            picture_file  = save_convict_picture(form.profile_image.data)
            convict.profile_image=picture_file
            img = ConvictImage.query.get_or_404(convict.id)
            loc = "D:\Flask\crimeassist\static\convict_pics"
            path1 = os.path.join(loc,img.image_file)
            os.remove(path1)
            img.image_file = picture_file            
        convict.name = form.name.data
        convict.crimes = form.crimes.data
        convict.dob = form.dob.data
        db.session.commit()
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
    convict_img = ConvictImage.query.get_or_404(convict.id)
    db.session.delete(convict)
    db.session.delete(convict_img)
    img1 = convict_img.image_file
    img2 = convict.profile_image
    loc = "D:\Flask\crimeassist\static\convict_pics"
    if img1 == img2 :
        path1 = os.path.join(loc,img1)
        os.remove(path1)
    else:
        path1 = os.path.join(loc,img1)
        os.remove(path1)
        path2 = os.path.join(loc,img2)
        os.remove(path2)
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
