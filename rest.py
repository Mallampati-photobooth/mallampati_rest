#!/usr/bin/env python

# python libs
import datetime, imghdr, os
import bottle
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, LargeBinary, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# custom packages
from mallampati_image.preprocessing import preprocess
from mallampati_detection.classify import classify

#==============================================================================
# App general config & helper functions
#==============================================================================
bottle.debug(True)
app = bottle.Bottle()

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
    processed_on = Column(DateTime, default = datetime.datetime.utcnow(),\
        nullable=False)
    mallampati_score = Column(Integer)
    valid_img = Column(Boolean, default = False)

    def __init__(self, original_img, processed_img):
        self.original_img = original_img
        self.processed_img = processed_img

    def __repr__(self):
        return '<Images %r %r>' % self.original_img, self.processed_img

Base.metadata.create_all(engine)


#==============================================================================
# Error handlers
#==============================================================================

@app.error(404)
def not_found(error):
    return {'error': 'Not found'}

@app.error(400)
def bad_request(error):
    return {'error': 'Bad request'}

@app.error(500)
def internal_server(error):
    return {'error': 'Internal server error'}

@app.error(403)
def forbidden(error):
    return {'error': 'Access forbidden'}

#==============================================================================
# REST routes
#==============================================================================

@app.post('/Images')
def upload_image():
    '''
    Uploads image.
    '''
    file = bottle.request.files.get('file')
    print(type(file))
    if file and allowed_file(file.filename)\
        and imghdr.what(file.file) in ALLOWED_EXTENSIONS:
        file.save(UPLOAD_FOLDER)
        preprocess(os.path.join(UPLOAD_FOLDER, file.filename), UPLOAD_FOLDER,
                   file.filename)
        with open(os.path.join(UPLOAD_FOLDER, file.filename), "rb")\
            as input_file:
                with open(os.path.join(UPLOAD_FOLDER,
                                       file.filename.rsplit('.', 1)[0]+".npy"),
                                       "rb") as gray_file:
                    img = input_file.read()
                    pp_img = gray_file.read()
                    db_entry = Images(img, pp_img)
                    session = Session()
                    session.add(db_entry)
                    session.commit()
                    session.close()
        os.remove(os.path.join(UPLOAD_FOLDER, file.filename))
        os.remove(os.path.join(UPLOAD_FOLDER, file.filename.rsplit('.', 1)[0]
            +".npy"))
    else:
        bottle.abort(400)

@app.get('/Images/<row:int>')
def retrieve_image(row):
    '''
    GETs the image from the blob
    '''
    session = Session()
    queried_row = session.query(Images).filter(Images.id == row).one()
    session.close()
    try:
        images = {'original.jpg':queried_row.original_img,
                  'processed.npy':queried_row.processed_img}
        for image in images:
            with open(os.path.join(UPLOAD_FOLDER,
                                   str(queried_row.id)+ "_"+image),
                                   "wb") as output_file:
                output_file.write(images[image])
         
        score = classify(os.path.join(UPLOAD_FOLDER, str(queried_row.id)
            + "_processed.npy"))

    except:  # pragma: no cover
        bottle.abort(400)
    
    return {'mallapati_score':str(score)}


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
