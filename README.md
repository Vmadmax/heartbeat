## Heartbeat &nbsp;[![Build Status](https://travis-ci.com/mowoe/heartbeat.svg?branch=master)](https://travis-ci.com/mowoe/heartbeat)



Heartbeat is a Face Recognition app, that you can upload Images to find more Images with the same face.

#### This Project *__can__* be used for evil shit, but the main Purpose was to show how easy and dangerous it is to build a mass surveillance service.

[:warning: This Demo](https://heartbeat.mowoe.com) is fed with Images from various social Media Sites, e.g. Instagram. You can upload a picture of yourself or anyone else and Heartbeat will try to find images with the same person on it.


## Deployment
Heartbeat needs an MySQL(-compatible) Database to store its faces and images. You need to create a user and a Database, the necessary tables are created by the peewee ORM itself.
##### The easiest way to deploy Heartbeat is by using docker:
```bash
sudo docker run --name heartbeat \
                -p 80:80 \
                -e DB_HOST=example.com \
                -e DB_PORT=3306 \
                -e DB_DATABASE=heartbeat \
                -e DB_PASSWORD=password\
                -e DB_USER=heartbeat \
                -e db_type=file \
                mowoe/heartbeat:latest
```
You can choose if you would like the uploaded pictures to be saved locallly (in the Docker container), or if you want them to be saved in an AWS S3 Bucket (is way cheaper than normal storage on VPS, as you quickly get into the Terabytes of images). To use Local space use the docker variable ```-e db_type=file```. To use the AWS S3 Storage change it to ```-e db_type=s3```. You also need to specify ```-e AWS_ACCESS_KEY=awskey```,```-e AWS_SECRET_KEY=aws_key``` and ```-e AWS_REGION=eu-central-1```(or any other region). Heartbeat supports other Bucket Storage Systems too, this is why you need to specify ```-e endpoint_url=http://s3.eu-central-1.amazonaws.com``` or any other Endpoint to an AWS S3 Storage like interface (like [min.io](https://min.io))

## Usage
### Upload an Image
To upload an Image via the API, you have to supply the URL to the image, direct Upload is currently only via the Frontend supported. You also have to supply an origin of the image, so it can later be traced back. If you have any other information about the image, you can supply them via the ```"img_info"``` Key. This is just a JSON Object with all Infos about the Image, which can also be used later for tracing the Image back.
```http
POST /api/add_image HTTP/1.1
Host: heartbeat.mowoe.com
Content-Type: application/json; charset=utf-8

{
  "img_url": "https://example.com/example.img",
  "img_info": "{'uploaded_date':128370}",
  "origin": "example.com"
}
```
### Request Work
To request Work form the Server you just have to supply a ```"work_type"``` Key, as Heartbeat theoretically also supports other recognition types than just Face Rec
```http
GET /api/request_work?work_type=face_recognition HTTP/1.1
Host: heartbeat.mowoe.com
```
### Submit Work
To submit the requested Work you have to supply the work and the image_id, that was retrieved when requesting work.
```http
POST /api/submit_work HTTP/1.1
Host: heartbeat.mowoe.com
Content-Type: application/json; charset=utf-8

{
  "result": "[representation of the face in a vector]",
  "image_id": "12345678",
  "work_type": "face_recognition"
}
```

