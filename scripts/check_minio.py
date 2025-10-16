from minio import Minio

client = Minio(
    'localhost:9000',
    access_key='minio_admin',
    secret_key='minio_password',
    secure=False
)

bucket_name = 'sales-data'

if client.bucket_exists(bucket_name):
    objects = list(client.list_objects(bucket_name, recursive=True))
    print(f"Fichiers dans '{bucket_name}': {len(objects)}")
    
    if objects:
        print("\nExemples (5 premiers):")
        for i, obj in enumerate(objects[:5]):
            print(f"  - {obj.object_name} ({obj.size} bytes)")
else:
    print(f"Bucket '{bucket_name}' n'existe pas")
