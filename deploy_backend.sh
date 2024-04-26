echo "Deploying Backend..."
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 638316737030.dkr.ecr.us-east-2.amazonaws.com
docker build -t beatbuddy-backend --platform linux/amd64 .  
docker tag beatbuddy-backend:latest 638316737030.dkr.ecr.us-east-2.amazonaws.com/beatbuddy-backend:latest
docker push 638316737030.dkr.ecr.us-east-2.amazonaws.com/beatbuddy-backend:latest
cd aws_deploy
eb deploy
