from flask import Flask, render_template, request, flash, jsonify, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from flask_migrate import Migrate
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2,csv,json,base64,os
import numpy as np
import csv
import subprocess

UPLOAD_FOLDER = 'uploads'
IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')


app = Flask(__name__)

# Database

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost:3306/nevar'
# Secret Key
app.config['SECRET_KEY'] = "nevarapi"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER


db = SQLAlchemy(app)
migrate=Migrate(app, db)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(IMAGE_UPLOAD_FOLDER):
    os.makedirs(IMAGE_UPLOAD_FOLDER)


    
#table-project
class PROJECT(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(2000), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Kolkata')))
    

    def __repr__(self):
        return '<Name %r>' % self.name
#table-folder
class folders(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(2000), nullable=False)
    date_added = db.Column(db.DateTime,default=datetime.now(pytz.timezone('Asia/Kolkata')))
    user_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)  # Update foreign key reference here

    user = db.relationship('PROJECT', backref='folders',foreign_keys=[user_id])

    def __repr__(self):
        return '<Upload %r>' % self.name


#table-upload
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(2000), nullable=False)
    image_filename = db.Column(db.String(100))
    bounding_boxes = db.Column(db.JSON)    
    date_added = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Asia/Kolkata')))
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)  # Define folder_id here

    folder = db.relationship('folders', backref='uploads', foreign_keys=[folder_id])

    def __repr__(self):
        return '<Upload %r>' % self.id

#table-polygon
class Polygon(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    polydata = db.Column(db.JSON)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'),nullable=False)
    upload = db.relationship('Upload', backref='polygon')
    def __repr__(self):
        return '<Polygon %r>' % self.id


class ProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[DataRequired()])
    submit = SubmitField("Submit")
    

class FolderForm(FlaskForm):
    name = StringField("Folder Name", validators=[DataRequired()])
    folder_upload = FileField("Upload a folder:", render_kw={'webkitdirectory': True})
    submit = SubmitField("Submit")


class FileForm(FlaskForm):
    name = StringField("File name", validators=[DataRequired()])
    image_file = FileField("Upload an image:", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif']),DataRequired()])
    text_file = FileField("Upload a text file:", validators=[FileAllowed(['txt']),DataRequired()])
    submit = SubmitField("Submit")


    
   
    
@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    project_to_delete = PROJECT.query.get_or_404(id)

    try:
        # Deleting related  folders and uploads
        for folder in project_to_delete.folders:
            for upload in folder.uploads:
                Polygon.query.filter_by(upload_id=upload.id).delete()
                db.session.delete(upload)
            db.session.delete(folder)

        db.session.delete(db.session.merge(project_to_delete))  
        db.session.commit()
        flash("Deleted successfully")
    except Exception as e:
        flash("Oops, delete failed: " + str(e))
        db.session.rollback()

    user = PROJECT.query.order_by(PROJECT.date_added)
    return render_template('Project.html', form=ProjectForm(), user=user)


       

@app.route('/deletefold/<int:id>', methods=['GET', 'POST'])
def deletefold(id):
    try:
        # Get the folder to delete
        foldertodelete = folders.query.get_or_404(id)

        # Delete associated uploads (images and text files) and polygons
        for upload in foldertodelete.uploads:
            # Delete associated polygons
            Polygon.query.filter_by(upload_id=upload.id).delete()

            # Delete associated uploads (images and text files)
            if upload.image_filename:
                image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', upload.image_filename)
                if os.path.exists(image_file_path):
                    os.remove(image_file_path)
            db.session.delete(upload)

        db.session.delete(foldertodelete)
        db.session.commit()
        flash("Deleted successfully")
    except Exception as e:
        db.session.rollback()
        flash("Oops, delete failed: " + str(e))

    return redirect(url_for('folder', id=foldertodelete.user_id))


@app.route('/deletefile/<int:folder_id>/<int:id>', methods=['GET', 'POST'])
def deletefile(folder_id, id):
    filetodelete = Upload.query.get_or_404(id)
    form = FileForm()

    try:
        # Delete associated polygons
        Polygon.query.filter_by(upload_id=id).delete()

        # Delete the file from the file system if it exists
        if filetodelete.image_filename:
            image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'images', filetodelete.image_filename)
            if os.path.exists(image_file_path):
                os.remove(image_file_path)

        # Delete the file entry from the database
        db.session.delete(filetodelete)
        db.session.commit()
        flash("Deleted file successfully")
    except Exception as e:
        flash("Oops, delete failed: " + str(e))
        db.session.rollback()

    return redirect(request.referrer)




    
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = ProjectForm()
    nametoupdate = PROJECT.query.get_or_404(id)

    if request.method == "POST":
        nametoupdate.name = request.form['name']

        try:
            db.session.commit()
            flash("Updated successfully")
            return redirect(url_for('name')) 
        except:
            flash("Update failed")
            return render_template('update.html', form=form, nametoupdate=nametoupdate, id=id)
    else:
        return render_template('update.html', form=form, nametoupdate=nametoupdate, id=id)

        
@app.route('/updatefold/<int:id>', methods=['GET', 'POST'])
def updatefold(id):
    form = FolderForm()
    foldertoupdate = folders.query.get_or_404(id)

    if request.method == "POST":
        foldertoupdate.name = request.form['name']

        try:
            db.session.commit()
            flash("Updated successfully")
            return redirect(url_for('folder', id=foldertoupdate.user_id))
        except:
            flash("Update failed")
            return render_template('updatefolder.html', form=form, foldertoupdate=foldertoupdate, id=id)
    else:
        return render_template('updatefolder.html', form=form, foldertoupdate=foldertoupdate, id=id)
   
        
@app.route('/', methods=['GET', 'POST'])
def name():
    name=None
    form = ProjectForm()
    if form.validate_on_submit():
        name = form.name.data
        new_user = PROJECT(name=name)
        db.session.add(new_user)
        db.session.commit()
        name = form.name.data
        form.name.data = ''
    
    user = PROJECT.query.order_by(PROJECT.date_added)
    return render_template('Project.html', form=form,name=name,user=user)



@app.route('/folder/<int:id>', methods=['GET','POST'])
def folder(id):
    form = FolderForm()
    
    if form.validate_on_submit():
        try:
            folder = form.name.data
            new_folder = folders(name=folder, user_id=id)
            db.session.add(new_folder)
            db.session.commit()
            flash("Folder created successfully")
            print("Form submitted")
            return redirect(url_for('folder', id=id))
        except Exception as e:
            flash(f"Error uploading folder: {str(e)}")
    user = folders.query.filter_by(user_id=id).order_by(folders.date_added)
    return render_template('folder.html', form=form, user=user, id=id)

@app.route('/upload_folder/<int:id>', methods=['GET','POST'])
def upload_folder(id):
    form = FolderForm()

    
    if form.validate_on_submit():
        try:
            folder_name = form.name.data
            new_folder = folders(name=folder_name, user_id=id)
            db.session.add(new_folder)
            db.session.commit()

            uploaded_files = request.files.getlist('folder_upload')
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

            for file in uploaded_files:
                file_path = os.path.join(folder_path, secure_filename(file.filename))
                file.save(file_path)

                # Construct the image path for the database
                image_path = os.path.join('images', folder_name, secure_filename(file.filename))

                # Create a new Upload entry and save it to the database
                new_file = Upload(name=secure_filename(file.filename), image_filename=image_path, folder_id=new_folder.id)
                db.session.add(new_file)
                db.session.commit()

            flash("Folder uploaded and saved successfully")
            return redirect(url_for('folder', id=id))

        except Exception as e:
            flash(f"Error uploading folder: {str(e)}")


        
    user = folders.query.filter_by(user_id=id).order_by(folders.date_added)
    return render_template('folder.html', form=form, user=user, id=id)

model = YOLO("yolov8n.pt")


@app.route('/save_existing_folder/<int:id>', methods=['POST'])
def save_existing_folder(id):
    try:
        existing_folder = request.files.getlist('folder_upload')

        if not existing_folder:
            flash("No files selected for existing folder")
            return redirect(request.referrer)

        # Get the folder name from the path
        folder_path = existing_folder[0].filename
        folder_name = os.path.basename(os.path.dirname(folder_path))

        new_folder = folders(name=folder_name, user_id=id)
        db.session.add(new_folder)
        db.session.commit()

        # Create the folder on the file system
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for file in existing_folder:
            file_path = os.path.join(folder_path, secure_filename(file.filename))
            file.save(file_path)
            
            # You can remove the YOLO-related code here

            new_file = Upload(
                name=secure_filename(file.filename),
                image_filename=file_path,
                folder_id=new_folder.id)
            db.session.add(new_file)
            db.session.commit()

        flash("Existing folder content saved successfully")

    except Exception as e:
        flash(f"Error saving existing folder content: {str(e)}")

    return redirect(request.referrer)

    try:
        existing_folder = request.files.getlist('folder_upload')

        if not existing_folder:
            flash("No files selected for existing folder")

        # Get the folder name from the path 
        folder_path = existing_folder[0].filename
        folder_name = os.path.basename(os.path.dirname(folder_path))

        new_folder = folders(name=folder_name, user_id=id)
        db.session.add(new_folder)
        db.session.commit()

        # Create the folder on the file system
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for file in existing_folder:
            file_path = os.path.join(folder_path, secure_filename(file.filename))
            file.save(file_path)
            
            # Perform YOLO
            yolo_model = YOLO("./yolov8n.pt")
            yolo_results = yolo_model.predict(source=file_path, project="project", save=True, save_txt=True,name=secure_filename(file.filename))
            image_name = secure_filename(file.filename)
            image_filename_parts = image_name.split('.')
            image_extension = image_filename_parts[-1]

            image_folder_name = f"{image_name.split('.')[0]}.{image_extension}"  
            image_folder_path = os.path.join('project', image_folder_name)
            labels_folder_path = os.path.join(image_folder_path, 'labels')
            text_file_path = os.path.join(labels_folder_path, f"{image_name.split('.')[0]}.txt")
            image_path = os.path.join('uploads', image_name, image_folder_name)

            # Read the bounding box information from the text file
            bounding_boxes = []

            with open(text_file_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    class_id, x, y, width, height = map(float, line.strip().split())
                    bounding_box = {'class_id': int(class_id), 'x': x, 'y': y, 'width': width, 'height': height}
                    bounding_boxes.append(bounding_box)
            
            
    
            new_file = Upload(
                name=secure_filename(file.filename),
                image_filename=file_path,
                bounding_boxes=bounding_boxes,
                folder_id=new_folder.id)
            db.session.add(new_file)
            db.session.commit()
    

        flash("Existing folder content saved successfully")

    except Exception as e:
        flash(f"Error saving existing folder content: {str(e)}")

    return redirect(request.referrer)



# Save file function
def save_file(file, folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
    file.save(file_path)
    return file_path

# Function to read text file content
def read_text_file_content(file):
    return file.read()
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Route for file upload
@app.route('/file/<int:id>', methods=['GET', 'POST'])
def file(id):
    name = None
    form = FileForm()

    folder = folders.query.get_or_404(id)

    if request.method == 'POST':
        
        if 'imagefile' in request.files:
            image_file = request.files['imagefile']
            print(image_file)
            name = request.form.get('name') 
            # Save image file
            if image_file and allowed_file(image_file.filename, allowed_extensions=['jpg', 'jpeg', 'png', 'gif']):
                image_filename = save_file(image_file, 'images')
                print("nameeeeeeeeeeeeeeeeeeeeee",name)
                upload_image = Upload(name=name, image_filename=image_filename, folder_id=id)
                db.session.add(upload_image)
                db.session.commit()
                flash("Image uploaded successfully")
    

    uploads = Upload.query.filter_by(folder_id=id).order_by(Upload.date_added).all()

    return render_template("filepage.html", id=id, form=form, uploads=uploads, folder=folder)



def parse_bounding_boxes(text_file):
    # Read text file content and parse the bounding box data
    bounding_boxes = []
    for line in text_file.readlines():
        class_id, x, y, width, height = map(float, line.strip().split())
        bounding_box = {'class_id': int(class_id), 'x': x, 'y': y, 'width': width, 'height': height}
        bounding_boxes.append(bounding_box)
    return bounding_boxes


def load_image(file_path):
    image = cv2.imread(file_path)
    return image





 

def get_original_image_dimensions(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Get the width and height of the image
    image_width, image_height = image.shape[1], image.shape[0]
    return image_width, image_height

def reverse_convert_bounding_boxes(processed_bounding_boxes, image_width, image_height, canvas_width=1200, canvas_height=700):
    if not isinstance(processed_bounding_boxes, list):
        raise ValueError("processed_bounding_boxes must be a list of dictionaries")

    # Calculate the scaling factors
    width_scale = canvas_width / image_width
    height_scale = canvas_height / image_height

    original_bounding_boxes = []

    for bbox in processed_bounding_boxes:
        if not isinstance(bbox, dict) or not all(key in bbox for key in ['id', 'x', 'y', 'width', 'height']):
            raise ValueError("Each element in processed_bounding_boxes must be a dictionary with keys 'id', 'x', 'y', 'width', 'height'")

        class_id = bbox['id']
        width = bbox['width'] / width_scale/( image_width)
        height = bbox['height'] / height_scale/ ( image_height)
        x = float((bbox['x'] / image_width / width_scale)+ width / 2) 
        y = float((bbox['y'] / image_height / height_scale)+ height / 2) 
        
        original_bounding_boxes.append({'class_id': class_id, 'x': x, 'y': y, 'width': width, 'height': height})
       
       
    return original_bounding_boxes


@app.route('/process/<int:id>', methods=['POST'])
def process(id):
    print(id)
    global image_data, bounding_boxes
    bounding_boxes = []

    try:
        upload_id = request.form.get('id')
        upload = Upload.query.get(upload_id)
        upImage=upload.image_filename
        print("______________________________________________")
        print(upload.image_filename)
        print("______________________________________________")

        # Read the image file content
        with open(upImage, 'rb') as image_file:
            image_content = image_file.read()

        # Read the bounding box data from the Upload model
        upload_id = request.form.get('id')
        upload = Upload.query.get(upload_id)
        
        if upload:
            bounding_boxes_json = upload.bounding_boxes
            if isinstance(bounding_boxes_json, list):
                bounding_boxes = bounding_boxes_json
            else:
                bounding_boxes = json.loads(bounding_boxes_json) if bounding_boxes_json else []
        
        # Process the image
        image = cv2.imdecode(np.frombuffer(image_content, np.uint8), cv2.IMREAD_COLOR)
        image_height, image_width, _ = image.shape
       
        

        canvas_width = 1200  
        canvas_height = 700  

        # Calculate scaling factors
        width_scale = canvas_width / image_width
        height_scale = canvas_height / image_height

        processed_bounding_boxes = []
        for bbox in bounding_boxes:  
            class_id = bbox['class_id']
            x = float((bbox['x'] - bbox['width'] / 2) * image_width * width_scale)
            y = float((bbox['y'] - bbox['height'] / 2) * image_height * height_scale)
            width = float(bbox['width'] * image_width * width_scale)
            height = float(bbox['height'] * image_height * height_scale)

            processed_bounding_boxes.append({'id': class_id, 'x': x, 'y': y, 'width': width, 'height': height})

        bounding_boxes = processed_bounding_boxes
        
        resized_image = cv2.resize(image, (canvas_width, canvas_height))

        _, processed_image = cv2.imencode('.jpg', resized_image)
        image_data = base64.b64encode(processed_image).decode('utf-8')

    except Exception as e:
        print(f"Error processing image and bounding boxes: {e}")
        # Clear the global image_data and bounding_boxes variables on error
        image_data = None
        bounding_boxes = []
    

    return render_template('Editingpad.html', image_data=image_data, bounding_boxes=bounding_boxes,id=upload_id)

def get_original_image_dimensions(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)

    # Get the width and height of the image
    image_width, image_height = image.shape[1], image.shape[0]
    return image_width, image_height

def reverse_convert_bounding_boxes(processed_bounding_boxes, image_width, image_height, canvas_width=1200, canvas_height=700):
    if not isinstance(processed_bounding_boxes, list):
        raise ValueError("processed_bounding_boxes must be a list of dictionaries")

    # Calculate the scaling factors
    width_scale = canvas_width / image_width
    height_scale = canvas_height / image_height

    original_bounding_boxes = []

    for bbox in processed_bounding_boxes:
        if not isinstance(bbox, dict) or not all(key in bbox for key in ['id', 'x', 'y', 'width', 'height']):
            raise ValueError("Each element in processed_bounding_boxes must be a dictionary with keys 'id', 'x', 'y', 'width', 'height'")

        class_id = bbox['id']
        width = bbox['width'] / width_scale/( image_width)
        height = bbox['height'] / height_scale/ ( image_height)
        x = float((bbox['x'] / image_width / width_scale)+ width / 2) 
        y = float((bbox['y'] / image_height / height_scale)+ height / 2) 
        
        original_bounding_boxes.append({'class_id': class_id, 'x': x, 'y': y, 'width': width, 'height': height})
       
       
    return original_bounding_boxes
    



@app.route('/saveboundingboxes/<int:id>', methods=['POST'])
def save_bounding_boxes(id):
    try:
        upload = Upload.query.filter_by(id=id).first()
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404

        data = request.get_json()
        
        # Extract bounding box data from the request
        bounding_boxes_data = data.get('bounding_boxes')  

        # Validate bounding box data
        if not isinstance(bounding_boxes_data, list) or not all(isinstance(bbox, dict) for bbox in bounding_boxes_data):
            return jsonify({'error': 'Bounding boxes must be a list of dictionaries'}), 400

        # Reverse convert the bounding boxes to original pixel coordinates
        image_path = upload.image_filename
        image_width, image_height = get_original_image_dimensions(image_path)
        original_bounding_boxes = reverse_convert_bounding_boxes(bounding_boxes_data, image_width, image_height)

        # Save the original bounding boxes data
        upload.bounding_boxes = original_bounding_boxes

        db.session.commit()
    
        return jsonify({'message': 'Bounding boxes saved successfully!'})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def pagenotfound(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def pagenotfound(e):
    return render_template("500.html"),500
@app.route('/error')
def error_page():
    return render_template('error.html')



def process_image_with_bounding_boxes(image, bounding_boxes, image_width, image_height):
    processed_image = image.copy()
    print("Bounding Boxes:", bounding_boxes)

    for bbox in bounding_boxes:
        x, y, width, height = int((bbox['x'] - bbox['width'] / 2) * image_width), int((bbox['y'] - bbox['height'] / 2) * image_height), int(bbox['width'] * image_width), int(bbox['height'] * image_height)
        cv2.rectangle(processed_image, (x, y), (x + width, y + height), (0, 255, 0), 2)
        
        # image height and width
        font_scale = min(image_height, image_width) / 1000.0
        font_scale = max(font_scale, 0.5) 
        
        # Draw ID 
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = f"ID: {bbox['class_id']}"
        print(text)
        font_thickness = max(int(font_scale * 2), 1)  
        
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = max(x, x + width - text_size[0])  
        text_y = max(y - 5, y - text_size[1])  
        cv2.putText(processed_image, text, (text_x, text_y), font, font_scale, (0, 0, 255), font_thickness, cv2.LINE_AA)

    return processed_image



# image generation
def generate_images(upload):
    try:
        folder_id = int(request.form.get('folder_id'))
        uploads = Upload.query.filter_by(folder_id=folder_id).all()

        for upload in uploads:
            # Retrieve image path and bounding box data from the database
            image_path = os.path.join(upload.image_filename)
            bounding_boxes = upload.bounding_boxes
            
           
            # Get the original image dimensions
            image_width, image_height = get_original_image_dimensions(image_path)
            
            print("image_width", image_width,"image_height",image_height)
            # Load the original image
            original_image = cv2.imread(image_path)

            # Process the image with bounding box merging logic
            processed_image = process_image_with_bounding_boxes(original_image, bounding_boxes,image_width, image_height)
            print("at pixels :",bounding_boxes)
            folder = folders.query.get(upload.folder_id)

            # Save the generated image to a different directory
            output_folder = os.path.join("OUTPUT", folder.name,upload.name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            output_filename = f"merged_{upload.name}"
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, processed_image)

        return jsonify({'success': True})

    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False}), 500
 
def format_bounding_box(bbox):
    class_id = bbox['class_id']
    x = bbox['x']
    y = bbox['y']
    width = bbox['width']
    height = bbox['height']
    return f"{class_id} {x} {y} {width} {height}"



# excel file generation 
def generatecsv(upload):
    try:
        folder_id = int(request.form.get('folder_id'))
        uploads = Upload.query.filter_by(folder_id=folder_id).all()

        # Create the CSV file path
        folder = folders.query.get(folder_id)
        output_folder = os.path.join("OUTPUT", folder.name)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        csv_output_filename = f"box_data_of_{folder.name}.csv"
        csv_output_path = os.path.join(output_folder, csv_output_filename)

        with open(csv_output_path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            # Write the header row
            csv_writer.writerow(['Name', 'Bounding Box Data'])
            
            for upload in uploads:
                bounding_box_list = upload.bounding_boxes 
                formatted_bboxes = [format_bounding_box(bbox) for bbox in bounding_box_list]
                formatted_bbox_data = '\n'.join(formatted_bboxes)
                csv_writer.writerow([upload.name, formatted_bbox_data])

        return jsonify({'success': True})

    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False}), 500

@app.route('/generate_all', methods=['POST'])
def generate_all():
    try:
        folder_id = int(request.form.get('folder_id'))
        uploads = Upload.query.filter_by(folder_id=folder_id).all()

        for upload in uploads:
            generate_images(upload)
            generatecsv(upload)
        flash("All files generated successfully!")
        return jsonify({'success': True})

    except Exception as e:
        flash("An error occurred during file generation: ")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/performsegmentation', methods=['POST'])
def perform_segmentation():
    # Extract data from the request
    data = request.json
    image_data = data.get('image_data')
    bounding_boxes = data.get('bounding_boxes')
    id = data.get('id')

    # Run the Python script
    try:
        subprocess.run(['python', 'run.py', image_data, bounding_boxes, id], check=True)
        # If the script runs successfully, return a success message
        return jsonify({'message': 'Segmentation performed successfully'})
    except subprocess.CalledProcessError as e:
        # If there's an error running the script, return an error message
        return jsonify({'error': f'Error running script: {e}'}), 500

@app.route('/savepolygon', methods=['POST'])
def save_polygon():
    data = request.get_json()
    polygon_data = data.get('polygonPoints')
    upload_id = data.get('id')
    print("idd",upload_id)
    try:    
        # Retrieve the image path from the Upload table using the upload_id
        upload = Upload.query.get(upload_id)
        if not upload:
            return jsonify({'error': 'Upload not found'}), 404

        image_path = upload.image_filename
        print("imagepath:",image_path)
        print(" ")
        print(" ")
        print(" ")
        print(" ")
        # Convert polygon data to YOLO format
        yolo_format_data = convert_polygon_to_yolo(polygon_data, image_path)

        # Save the YOLO-formatted polygon data to the database
        polygon = Polygon(polydata=yolo_format_data, upload_id=upload_id)
        db.session.add(polygon)
        db.session.commit()

        return jsonify({'message': 'Polygon saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    




    

def convert_polygon_to_yolo(polygon_data, image_path, canvas_width=1200, canvas_height=700):
    # Get the original image dimensions
    image_width, image_height = get_original_image_dimensions(image_path)
    print("image_width", image_width)
    print("image_height", image_height)
    canvas_width = 1200
    canvas_height = 700
    width_scale = canvas_width / image_width
    height_scale = canvas_height / image_height
    # Convert polygon data to YOLO format
    yolo_format_data = []

    for polygon in polygon_data:
        print("polyyyyyyyyyyyyyy", polygon)
        # Extract x and y coordinates of vertices
        x = polygon.get('x')
        y = polygon.get('y')

        if x is not None and y is not None:
            print(" ")
            print(" ")
            print("X coordinate:", x)
            print("Y coordinate:", y)

            # Calculate the center of the polygon
            x_center_normalized = x / image_width
            y_center_normalized = y / image_height

            # Append the polygon data in YOLO format
            yolo_format_data.append({'x': x_center_normalized, 'y': y_center_normalized})

    return yolo_format_data

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)