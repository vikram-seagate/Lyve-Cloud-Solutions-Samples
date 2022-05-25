# fast-stream

The solution is intended to be able to stream media from Lyve Cloud fluently, with tracking of which media
is consumed often and therefore considered to be popular. The solution would then cache the front-part of popular
medias to allow for faster streaming. 

The solution is intended to use a SQLite database to keep track of requests and be able to be well packaged into a Docker image. The solution is however incomplete. 

## Setup 
After pulling the solution from github, run `npm init`. 

The access key, secret key and region of the Lyve Cloud S3 must the be set as environment variables `AWS_REGION`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

The solution can then be ran using `npm run backend-start`. 

An accompanying front-end to test video viewing is available at "http://localhost:3000/video" after running `npm run dev`