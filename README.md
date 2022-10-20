# stc-backend
Salim Toys Company Backend App

## Setting Up
### Virtualenv and Dependencies
Make sure that you are using at least python `3.7`

activate virtual env
```
source venv/bin/activate
```

To install requirement
```
make lib.install
```

### AWS config
Create `.env` file with aws credentials
```
FLASK_APP="main.py" #This is a must have
AWS_ACCESS_KEY_ID="hello"
AWS_SECRET_ACCESS_KEY="world"
AWS_TABLE_REGION="ap-southeast-2"
SECRET_KEY="magic"

# HS-Toys.mdb table name that we will extract from
PRODUCT_TABLE_NAME="Swatch1"

# if set to "1" will enable authentication, if not, will bypass JWT auth
AUTH_ENABLED="1"
```
Alternatively, we can import the aws credentials in your `~/.aws/credentials`
by changing this code
```
session = boto3.Session(profile_name='<your-aws-config-profile-name-here>')
dynamodb_client = session.client('dynamodb')
```

### Start the server
```
make run
```

### Deactivate Virtual Environment
To deactivate virtual env
```
deactivate
```

### Installing new python3 lib
After installing new library with
```
pip3 install <library_name>
```
dont forget to update `requirements.txt` before you commit
```
make lib.gen
```


### Generate new csv
Pass the mdb file to `/data` and run, the file has to be named `HS-toys.mdb`
```
make data
```


### Build docker image
Build the docker image with docker compose (includes .env var)
```
make build
```

Build and run manually (this one does not include .env var)
```
docker build -t flask-docker:latest . 
docker run -p 5000:5000 flask-docker  
```