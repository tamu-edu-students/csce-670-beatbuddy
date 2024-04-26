echo "Deploying Backend..."
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 638316737030.dkr.ecr.us-east-2.amazonaws.com
docker build -t beatbuddy-backend_clip .
docker tag beatbuddy-backend_clip:latest 638316737030.dkr.ecr.us-east-2.amazonaws.com/beatbuddy-backend_clip:latest
docker push 638316737030.dkr.ecr.us-east-2.amazonaws.com/beatbuddy-backend_clip:latest
cd aws_deploy
eb deploy
