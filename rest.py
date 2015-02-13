#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime, imghdr, os
from bottle import route, run, request, abort, error, debug
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, LargeBinary, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#==============================================================================
# App general config & helper functions
#==============================================================================
debug(True)
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#==============================================================================
# SQL configuration
#==============================================================================
engine = create_engine('sqlite:///images.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Images(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)    
    original_img = Column(LargeBinary)
    processed_img = Column(LargeBinary)
    uploaded_on = Column(DateTime, default = datetime.datetime.utcnow(),\
        nullable=False)
    processed_on = Column(DateTime)
    mallampati_score = Column(Integer)
    valid_img = Column(Boolean, default = False)
    
    def __init__(self, original_img):
        self.original_img = original_img

    def __repr__(self):
            return '<Images %r>' % self.original_img

Base.metadata.create_all(engine)


#==============================================================================
# Error handlers
#==============================================================================

@error(404)
def not_found(error):
    return {'error': 'Not found'}

@error(400)
def bad_request(error):
    return {'error': 'Bad request'}

@error(500)
def internal_server(error):
    return {'error': 'Internal server error'}

@error(403)
def forbidden(error):
    return {'error': 'Access forbidden'}

    
#==============================================================================
# REST routes
#==============================================================================

@route('/Images', method= 'POST') 
def upload_image():
    '''
    Uploads image
    '''
    file = request.files.get('file')
    print(type(file))
    if file and allowed_file(file.filename)\
        and imghdr.what(file.file) in ALLOWED_EXTENSIONS:
        file.save(UPLOAD_FOLDER)
        with open(os.path.join(UPLOAD_FOLDER, file.filename), "rb")\
            as input_file:
            data = input_file.read()
            db_image = Images(data)
            session = Session()
            session.add(db_image)
            session.commit()
            session.close()
        os.remove(os.path.join(UPLOAD_FOLDER, file.filename))
    else:
        abort(400)
        
@route('/Images/<row:int>', method= 'GET')
def upload_metadata(row):
    '''
    GETs the image from the blob
    '''
    session = Session()
    queried_row = session.query(Images).filter(Images.id == row).one()
    session.close()
    try:
        with open(os.path.join(UPLOAD_FOLDER,\
        str(queried_row.id) + ".jpg"), "wb") as output_file:
            output_file.write(queried_row.original_img)
    except:
        abort(400)


run(host='localhost', port=5000)