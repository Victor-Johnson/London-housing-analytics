import duckdb
from dotenv import load_dotenv
import os

load_dotenv()


AWS_KEY_ID = os.getenv("AWS_KEY_ID")
AWS_SECRET = os.getenv("AWS_SECRET")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET = os.getenv("AWS_BUCKET")
STATE = os.getenv("DEBUG_MODE")

if STATE == True:
    print("DEBUG MODE : ")
    print(f"Region: {AWS_REGION}")
    print(f"Bucket: {AWS_BUCKET}")
    print(f"Key loaded: {'yes' if AWS_KEY_ID else 'NO - check your .env'}")
else:
    print("NO DEBUG")


try:
    con = duckdb.connect()

    con.execute(f"""
        INSTALL httpfs;
        LOAD httpfs;
        CREATE SECRET aws_secret (
            TYPE S3,
            KEY_ID '{AWS_KEY_ID}',
            SECRET '{AWS_SECRET}',
            REGION '{AWS_REGION}'
        );
    """)

    result = con.execute(f"""
        SELECT * FROM glob('s3://{AWS_BUCKET}/**')
    """).fetchall()

    for f in result:
        print(f)

except Exception as e:
    print(f"Failed: {e}")