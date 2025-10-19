# OpenMetadata JWT Keys Configuration

This directory contains JWT keys for OpenMetadata authentication.

## Generate Keys

To generate new JWT keys for production:

```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Generate public key
openssl rsa -in private_key.pem -pubout -outform DER -out public_key.der

# Generate private key in DER format
openssl pkcs8 -topk8 -inform PEM -outform DER -in private_key.pem -out private_key.der -nocrypt
```

## Default Keys (Development Only)

For development purposes, OpenMetadata will generate default keys automatically on first startup.

⚠️ **WARNING**: Do not use default keys in production!

## Files

- `public_key.der`: Public key for JWT verification (DER format)
- `private_key.der`: Private key for JWT signing (DER format)
- `private_key.pem`: Private key in PEM format (optional, for reference)

## Permissions

Ensure proper file permissions:

```bash
chmod 600 private_key.der private_key.pem
chmod 644 public_key.der
```

## Documentation

- [OpenMetadata Authentication](https://docs.open-metadata.org/v1.10.x/deployment/security/enable-jwt-tokens)
- [JWT Configuration](https://docs.open-metadata.org/v1.10.x/deployment/security/jwt-configuration)
