echo "Deploying Frontend..."
cd web/frontend
export REACT_APP_API_URL=/api
npm run build
aws s3 sync build/ s3://beatbuddy-frontend --acl public-read