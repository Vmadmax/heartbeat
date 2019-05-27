from flask import Flask, Response, request, redirect, url_for, make_response
import json
from werkzeug.utils import secure_filename
import os
import time
import hashlib
import heartbeat_database
import thread

UPLOAD_FOLDER = './uploaded_pics/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class EndpointAction(object):
    def __init__(self,action):
        self.action = action

    def __call__(self, **args):
        self.response = self.action(args)
        return self.response

class Server(object):
    def __init__(self, hdb, port=9721,bind_address='0.0.0.0'):
        self.port = port
        self.bind_address = bind_address
        self.webapp = Flask(__name__)
        self.HeartDB = hdb

    def setup(self):
        self.webapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        self.webapp.add_url_rule('/add_image', "image_add", EndpointAction(self.add_image))
        self.webapp.add_url_rule('/add_image_via_file', "file_add", EndpointAction(self.add_file), methods=['POST'])
        self.webapp.add_url_rule('/request_work/<table>', "request_work", EndpointAction(self.request_work))
        self.webapp.add_url_rule('/get_image/<id>', "get_image", EndpointAction(self.get_image))
        self.webapp.add_url_rule('/submit_work',"submit_work",EndpointAction(self.submit_work))

    def constr_resp(self,status,reason="healthy"):
        return json.dumps({'status':status, 'reason':reason})

    def add_file(self,args):
        start = time.time()
        if 'file' not in request.files:
            print("This request took {} seconds".format(str(time.time()-start)))
            return self.constr_resp("error","no file part")
        file = request.files['file']
        if file.filename == '':
            print("This request took {} seconds".format(str(time.time()-start)))
            return self.constr_resp("error","no file supplied")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            hash_object = hashlib.sha256(str(time.time()).encode())
            hex_dig = hash_object.hexdigest()
            new_filename = str(hex_dig) + "." + filename.split(".")[-1]
            file.save(os.path.join(self.webapp.config['UPLOAD_FOLDER'], new_filename))
            print("This request took {} seconds".format(str(time.time()-start)))
            thread.start_new_thread(self.HeartDB.add_image, (new_filename,"unknown"))
            return self.constr_resp("success")
        
    def add_image(self,args):
        img_url = request.args.get('img_url')
        information = request.args.get('img_info')
        if type(img_url) == type(None) or type(information) == type(None):
            response = Response(self.constr_resp("error","No url or Image provided"), status=401, headers={})
            return response
        information = json.loads(information)
            
        response = Response(self.constr_resp("success"), status=200, headers={})
        return response

    def get_image(self,args):
        imgid = args['id']
        filename = self.HeartDB.get_filename_from_id(imgid)
        print("filename {}".format(filename))
        headers = {"Content-Disposition": "attachment; filename=%s" % filename}
        with open(os.path.join(self.webapp.config['UPLOAD_FOLDER'], filename), 'r') as f:
            body = f.read()
        return make_response((body, headers))

    def request_work(self,table):
        table = table["table"]
        print("Table: {}".format(table))
        resp_id = self.HeartDB.get_work(table)
        return Response(self.constr_resp(resp_id),status=200)

    def submit_work(self,args):
        try:
            imageid = request.args.get('imageid')
            table = request.args.get('table')
            info = request.args.get('info')
        except Exception as e:
            print(e)
            return Response(self.constr_resp("Error parsing"),status=400)
        self.HeartDB.submit_work(table, imageid, info)
        return Response(self.constr_resp("done"),status=200)

    def listen(self):
        self.webapp.run(port=self.port,host=self.bind_address)

class Client(object):
    def __init__(self):
        pass

if __name__ == "__main__":
    hdb = heartbeat_database.HeartDB()
    hdb.init_tables(["face_recognition","face_encodings"])
    hdb.connect()
    serv = Server(hdb)
    serv.setup()
    serv.listen()