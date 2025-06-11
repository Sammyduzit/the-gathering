from app.core.config import settings

print("Testing config:")
print(f"App name: {settings.APP_NAME}")
print(f"Database URL: {settings.DATABASE_URL}")
print(f"Secret Key: {settings.SECRET_KEY}")
print(f"Debug: {settings.DEBUG}")
print("All checked!")