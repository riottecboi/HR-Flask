
# HR-Employee Dashboard

This project is building a server for HR - Employee Dashboard which control an employee inside company and edit their profiles




## Tech Stack

**Client:** HTML, CSS, Javascript (chartjs)

**Server:** Python, Flask, Mysql




## Environment Variables

To run this project, you will need to add the following environment variables to your settings file

`SECRET_KEY`
  this using for Flask form security

`AWS_BUCKET` S3 bucket name

`AWS_ACCESS_KEY_ID` S3 access key ID

`AWS_SECRET_ACCESS_KEY` S3 secret key

`SQLALCHEMY_DATABASE_URI` it could be set as format

 'mysql+pymysql://xxxx:3306/employee?user=xxx&password=xxx'

`POOL_SIZE` could set at 1

`POOL_RECYCLE` could set at 60

`TMP_PATH` set '/tmp'


## Installation

When you creating new instance, please do this way to install all necessary packages for server

```bash
  cd HR-Flask
  python3 -m pip install -r requirements.txt
  python3 -m pip install markupsafe==2.0.1

  python3 server.py
```

On AWS console, please be sure, the security group of instance have to open for HTTP (80) and HTTPS(433) and SSH (22)

On RDS, the database also need to be set up for security group for Mysql(3306) and SSH(22)

On S3, should add policy like this 

```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::leekylie-bucket/*",
                "arn:aws:s3:::leekylie-bucket"
            ]
        }
    ]
}

```

AWS ACCESS_KEY and AWS_SCERET_ID should be grant permission on https://us-east-1.console.aws.amazon.com/iam/home#/users/hr-dashboard?section=permissions

with 2 permissions

```bash
AmazonRDSFullAccess
AmazonS3FullAccess

```


## Demo

http://employee-dashboard.spacey.tech/login




## Authors

- [@riottecboi](https://github.com/riottecboi)
- riottecboi@gmail.com

